import re
import time
from contextlib import contextmanager, redirect_stdout
from io import StringIO

import streamlit as st

import shared.helpers as hlp
from shared.sessionstate import ss_get, ss_set

# Initialize session state variables
if "run_pipeline_clicked" not in st.session_state:
    ss_set("run_pipeline_clicked", False)

if "job_id" not in st.session_state:
    ss_set("job_id", "")


@contextmanager
def st_capture(output_func):
    try:
        with StringIO() as stdout, redirect_stdout(stdout):
            old_write = stdout.write

            def new_write(string):
                ret = old_write(string)
                output_func(stdout.getvalue())
                return ret

            stdout.write = new_write
            yield
    except Exception as e:
        st.error(str(e))


def get_path_to_script(selected_pipeline, selected_project, selected="all"):
    NX_shared_path = "/data/scratch/shared/RSE/NF-project-configurations/"
    # e.g., /data/scratch/shared/RSE/NF-project-configurations/epi2me-human-variation/nf-long-reads/scripts
    path = NX_shared_path + selected_pipeline + "/" + selected_project + "/scripts/"
    if selected == "all":
        path = path + "launch_samples.sh"
    elif selected == "demo":
        path = path + "launch_demo.sh"
    else:
        path = path + "launch_sample_analysis.sh"
        raise Exception("No support for sample runs on customised entries")
    return path

    # --env --params
    # --work-dir
    # --outdir


# launch command based on the project
def pipe_cmd(
    username,
    selected_pipeline=None,
    selected_project=None,
    cmd_num=0,
    selected_samples="all",
    work_dir="work",
    output_dir="output",
):
    if cmd_num == 0:
        path_to_script = get_path_to_script(selected_pipeline, selected_project, selected_samples)
        # cmake sure to cd before launching the script
        cmd_pipeline = f"mkdir -p {work_dir}/logs; \n"
        cmd_pipeline += f"cd {work_dir}; \n"
        if selected_samples == "demo":  # use sbatch
            # sbatch launch_demo.sh work_dir output_dir custom_config.config /data/rds/DIT/SCICOM/SCRSE/shared/conda/nextflow_env
            cmd_pipeline += f"sbatch {path_to_script} {work_dir} {output_dir}"
        if selected_samples == "all":  # use bash
            ##./your_script.sh --env "/my/custom/env" --work-dir "my_work" --outdir "my_output" --config "my_config" --params "parans.json"
            # Usage:
            # bash launch_batch_analysis.sh \
            #     --work-dir "workdir" \
            #     --outdir "output" \
            #     --env "/data/rds/DIT/SCICOM/SCRSE/shared/conda/nextflow_env" \
            #     --params "/data/params/parameters.json" \
            #     --config "custom_config.config"
            cmd_pipeline += f"sbatch {path_to_script} --work-dir {work_dir} --outdir {output_dir}"
        return cmd_pipeline
    elif cmd_num == 1:
        cmd_pipeline = f"squeue -u {username}"
        return cmd_pipeline
    elif cmd_num == 2:
        cmd_pipeline = f"sacct --user {username} --format UID,User,JobID,JobName,Submit,Elapsed,Partition,NNodes,NCPUS,TotalCPU,CPUTime,ReqMem,MaxRSS,WorkDir,State,Account,AllocTres -P"
        return cmd_pipeline
    elif cmd_num == 3:
        cmd_pipeline = "echo hello from nextflow-on-Alma app"
        return cmd_pipeline


def tab(username, MY_SSH, selected_pipeline, selected_project, selected_samples="all", work_dir="work", output_dir="output"):
    cols = st.columns([1, 1, 1])
    with cols[0]:
        username = st.text_input(
            "Username(s):",
            username,
            key="username-mod",
            help="Enter your username e.g. ralcraft",
        )

    def run_nextflow():  # username, MY_SSH, selected_pipeline, selected_project):
        # return True  # temporary
        cmd_pipeline = pipe_cmd(
            username,
            selected_pipeline,
            selected_project,
            cmd_num=0,
            selected_samples=selected_samples,
            output_dir=output_dir,
            work_dir=work_dir,
        )
        st.code(cmd_pipeline)
        _dict = MY_SSH.run_cmd(cmd_pipeline)
        # process output to get job id
        match = re.search(r"Submitted batch job (\d+)", _dict["output"])
        job_id = match.group(1) if match else None
        st.success(f"✅ Job ID: {job_id}")
        return job_id
        # to do, we need to wait for an asynchronous answer regarding slurm?

    tabP, tabL, tabQ = st.tabs(["Run pipeline", "Check logs", "Check queues"])
    with tabL:
        if st.button("Get Logs"):
            tO, tE = st.tabs(["Output", "Error"])
            with tO:
                outputO = st.empty()
            with tE:
                outputE = st.empty()
            with st.spinner("Fetching...", show_time=True):
                try:
                    with hlp.st_capture(outputO.code):
                        print("Output log", f"{work_dir}/logs/cosmx.txt")  # todo: need to rename log files?
                        txtl = MY_SSH.read_file(f"{work_dir}/logs/cosmx.txt")
                        print(txtl)
                    with hlp.st_capture(outputE.code):
                        print("Error log", f"{work_dir}/logs/cosmx.err")
                        txte = MY_SSH.read_file(f"{work_dir}/logs/cosmx.err")
                        print(txte)
                except Exception as e:
                    st.error(f"Error {e}")
    with tabQ:
        if st.button("Check slurm queues"):
            output = st.empty()
            with st.spinner("Checking...", show_time=True):
                with hlp.st_capture(output.code):
                    cmd_pipeline = pipe_cmd(username, None, None, cmd_num=1)
                    print("Executing command\n", cmd_pipeline)
                    try:
                        results = MY_SSH.run_cmd(cmd_pipeline)
                        if results["err"] != None:
                            st.error(results["err"])
                        else:
                            print("------------------------------")
                            print(results["output"])
                    except Exception as e:
                        st.error(f"Error {e}")
    with tabP:
        # disable button once the user click a first time. by default it gets disabled after calling the callback
        v = st.button(f"Run the selected nextflow pipeline for {username}", disabled=ss_get("run_pipeline_clicked"))
        if ss_get("job_id") != "":
            job_id = ss_get("job_id")
            st.success(f"Running Job ID: {job_id}")
        if v:
            ss_set("run_pipeline_clicked", True)
            output = st.empty()
            with st.spinner("Starting...", show_time=True):
                with hlp.st_capture(output.code):
                    try:
                        ss_set("job_id", run_nextflow())
                    except Exception as e:
                        st.error(f"Error {e}")
