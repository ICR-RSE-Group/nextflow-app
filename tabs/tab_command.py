import os
import re
import time
from io import StringIO

import streamlit as st

import shared.helpers as hlp
from shared.sessionstate import retrieve_all_from_ss, ss_get, ss_set

# Initialize session state variables
if "run_pipeline_clicked" not in st.session_state:
    ss_set("run_pipeline_clicked", False)

if "job_id" not in st.session_state:
    ss_set("job_id", "")
# pull saved values if set, otherwise set to defaults
(
    OK,
    MY_SSH,
    username,
    GROUPS,
    GROUP,
    SCRATCH,
    RDS,
    PROJECT,
    SAMPLE,
    PIPELINE,
) = retrieve_all_from_ss()


def get_path_to_script(selected_pipeline, selected_project, selected="all"):
    NX_SHARED_PATH = "/data/scratch/shared/RSE/NF-project-configurations"
    # e.g., /data/scratch/shared/RSE/NF-project-configurations/epi2me-human-variation/nf-long-reads/scripts
    base_path = os.path.join(NX_SHARED_PATH, selected_pipeline, selected_project, "scripts")

    script_mapping = {
        "all": "launch_samples.sh",
        "demo": "launch_demo.sh",
        "single": "launch_sample_analysis.sh",  # not yet supported
    }

    if selected in script_mapping:
        return os.path.join(base_path, script_mapping[selected])

    raise ValueError(f"Invalid selection '{selected}'. Only 'all' and 'demo' are supported.")


# launch command based on the project
def pipe_cmd(
    username,
    selected_pipeline="",
    selected_project="",
    cmd_num=0,
    selected_samples="all",
    work_dir="work",
    output_dir="output",
):
    def get_pipeline_command():
        """Generate the pipeline execution command based on the sample selection."""
        path_to_script = get_path_to_script(selected_pipeline, selected_project, selected_samples)

        cmd_pipeline = f"""
        mkdir -p {work_dir}/logs
        cd {work_dir}
        """
        # not sure if this is the best thing-using job id for filenamne
        log_out = f"{work_dir}/logs/%j.out"
        log_err = f"{work_dir}/logs/%j.err"

        if selected_samples == "demo":
            cmd_pipeline += f"sbatch  -o {log_out} -e {log_err} {path_to_script} {work_dir} {output_dir}"
        elif selected_samples == "all":
            cmd_pipeline += f"sbatch  -o {log_out} -e {log_err} {path_to_script} --work-dir {work_dir} --outdir {output_dir}"
            ##./your_script.sh --env "/my/custom/env" --work-dir "my_work" --outdir "my_output" --config "my_config" --params "parans.json"
            # Usage:
            # bash launch_batch_analysis.sh \
            #     --work-dir "workdir" \
            #     --outdir "output" \
            #     --env "/data/rds/DIT/SCICOM/SCRSE/shared/conda/nextflow_env" \
            #     --params "/data/params/parameters.json" \
            #     --config "custom_config.config"

        return cmd_pipeline.strip()

    # Command mappings
    command_map = {
        0: get_pipeline_command(),
        1: f"squeue -u {username}",
        2: (
            f"sacct --user {username} "
            "--format UID,User,JobID,JobName,Submit,Elapsed,Partition,"
            "NNodes,NCPUS,TotalCPU,CPUTime,ReqMem,MaxRSS,WorkDir,State,"
            "Account,AllocTres -P"
        ),
        3: "echo hello from nextflow-on-Alma app",
    }

    # Return the corresponding command
    return command_map.get(cmd_num, "echo 'Invalid command number'")


def display_log(title, log_path, output_container):
    """function to display log content."""
    try:
        with hlp.st_capture(output_container.code):
            print(f"{title} log:", log_path)
            log_content = MY_SSH.read_file(log_path)
            print(log_content)
    except Exception as e:
        st.error(f"Failed to read {title.lower()} log: {e}")


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
            job_id = ss_get("job_id", "")
            if job_id == "":
                st.error("No job was launched yet")
            else:
                log_out = f"{work_dir}/logs/{job_id}.out"
                log_err = f"{work_dir}/logs/{job_id}.err"
                tO, tE = st.tabs(["Output", "Error"])
                outputO, outputE = tO.empty(), tE.empty()
                with st.spinner("Fetching...", show_time=True):
                    display_log("Output", log_out, outputO)
                    display_log("Error", log_err, outputE)

    with tabQ:
        if st.button("Check slurm queues"):
            output = st.empty()
            with st.spinner("Checking...", show_time=True):
                with hlp.st_capture(output.code):
                    cmd_pipeline = pipe_cmd(username, cmd_num=1)
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
        # disable button once the user clicks a first time. by default it gets disabled after calling the callback
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
