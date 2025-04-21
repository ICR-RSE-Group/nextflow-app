import re

import streamlit as st

import shared.command_helper as cmd_hlp
import shared.helpers as hlp
from shared.sessionstate import ss_get


def tab(
    username,
    MY_SSH,
    selected_pipeline,
    selected_project,
    selected_samples="all",
    work_dir="work",
    output_dir="output",
    custom_sample_list=[],
):
    # Initialize session vars only if not already set
    if "JOB_ID" not in st.session_state:
        st.session_state["JOB_ID"] = None
    if "run_pipeline_clicked" not in st.session_state:
        st.session_state["run_pipeline_clicked"] = False

    # UI to update username
    cols = st.columns([1, 1, 1])
    with cols[0]:
        username = st.text_input("Username(s):", username, key="username-mod")

    def display_log(title, log_path, output_container):
        try:
            log_file = MY_SSH.read_file(log_path)
            log_content = log_file.read() if hasattr(log_file, "read") else str(log_file)
            output_container.code(log_content, language="bash")
        except Exception as e:
            st.error(f"❌ Failed to read {title.lower()} log: {e}")

    # ---------- RUN PIPELINE ----------
    def run_nextflow():
        cmd_pipeline = cmd_hlp.pipe_cmd(
            username,
            selected_pipeline,
            selected_project,
            cmd_num=0,
            selected_samples=selected_samples,
            output_dir=output_dir,
            work_dir=work_dir,
            custom_sample_list=custom_sample_list,
        )
        st.code(cmd_pipeline)
        result = MY_SSH.run_cmd(cmd_pipeline)
        match = re.search(r"Submitted batch job (\d+)", result["output"])
        job_id = match.group(1) if match else None
        st.session_state["JOB_ID"] = job_id
        st.success(f"✅ Job submitted. ID: {job_id}")
        return job_id

    # ---------- TABS ----------
    tabP, tabL, tabQ = st.tabs(["Run pipeline", "Check logs", "Check queues"])

    # ---------- Run pipeline tab ----------
    with tabP:
        if st.button(f"Run the selected Nextflow pipeline for {username}", disabled=st.session_state["run_pipeline_clicked"]):
            st.session_state["run_pipeline_clicked"] = True
            with st.spinner("Starting pipeline..."):
                try:
                    run_nextflow()
                except Exception as e:
                    st.error(f"Pipeline error: {e}")

        if st.session_state["JOB_ID"]:
            st.success(f"Running Job ID: {st.session_state['JOB_ID']}")
    # ---------- Logs queues ----------
    with tabQ:
        if st.button("Check slurm queues"):
            output = st.empty()
            with st.spinner("Checking...", show_time=True):
                with hlp.st_capture(output.code):
                    cmd_pipeline = cmd_hlp.pipe_cmd(username, cmd_num=1)
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
    # ---------- Logs tab ----------
    with tabL:
        if st.button("Get Logs"):
            job_id = "17381098"
            st.write(st.session_state.get("JOB_ID"), ss_get("JOB_ID"))
            job_id = st.session_state.get("JOB_ID")
            if not job_id:
                st.error("No job was launched yet")
            else:
                log_out = f"{work_dir}/logs/{job_id}.out"
                log_err = f"{work_dir}/logs/{job_id}.err"
                tO, tE = st.tabs(["Output", "Error"])
                outputO, outputE = tO.empty(), tE.empty()
                with st.spinner("Fetching logs..."):
                    display_log("Output", log_out, outputO)
                    display_log("Error", log_err, outputE)
