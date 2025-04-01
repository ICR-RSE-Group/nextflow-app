import re

import streamlit as st

import shared.command_helper as cmd_hlp
import shared.helpers as hlp
from shared.sessionstate import retrieve_all_from_ss, ss_get, ss_set

# pull saved values if set, otherwise set to defaults
ss_values = retrieve_all_from_ss()
OK = ss_values["OK"]
MY_SSH = ss_values["MY_SSH"]
username = ss_values["user_name"]
server = ss_values["server"]
GROUP = ss_values["GROUP"]
GROUPS = ss_values["GROUPS"]
SCRATCH = ss_values["SCRATCH"]
RDS = ss_values["RDS"]
SAMPLE = ss_values["SAMPLE"]
PIPELINE = ss_values["PIPELINE"]
password = ss_values["password"]
PROJECT = ss_values["PROJECT"]
JOB_ID = ss_values["JOB_ID"]
WORKDIR = ss_values["WORK_DIR"]
OUTPUT_DIR = ss_values["OUTPUT_DIR"]
run_pipeline_clicked = ss_values["run_pipeline_clicked"]


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
    JOB_ID = ss_values["JOB_ID"]

    cols = st.columns([1, 1, 1])
    with cols[0]:
        username = st.text_input(
            "Username(s):",
            username,
            key="username-mod",
            help="Enter your username e.g. ralcraft",
        )

    def run_nextflow():
        cmd_pipeline = cmd_hlp.pipe_cmd(
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
        JOB_ID = match.group(1) if match else None
        st.success(f"✅ Job ID: {JOB_ID}")
        return JOB_ID
        # to do, we need to wait for an asynchronous answer regarding slurm?

    tabP, tabL, tabQ = st.tabs(["Run pipeline", "Check logs", "Check queues"])
    with tabL:
        if st.button("Get Logs"):
            if JOB_ID == "":
                st.error("No job was launched yet")
            else:
                log_out = f"{work_dir}/logs/{JOB_ID}.out"
                log_err = f"{work_dir}/logs/{JOB_ID}.err"
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
    with tabP:
        # disable button once the user clicks a first time. by default it gets disabled after calling the callback
        clicked = st.button(f"Run the selected nextflow pipeline for {username}", disabled=ss_get("run_pipeline_clicked"))
        JOB_ID = ss_get("JOB_ID")
        if JOB_ID is not None:
            st.success(f"Running Job ID: {JOB_ID}")
        if clicked:
            ss_set("run_pipeline_clicked", True)
            output = st.empty()
            with st.spinner("Starting...", show_time=True):
                with hlp.st_capture(output.code):
                    try:
                        JOB_ID = run_nextflow()
                        ss_set("JOB_ID", JOB_ID)
                    except Exception as e:
                        st.error(f"Error {e}")
