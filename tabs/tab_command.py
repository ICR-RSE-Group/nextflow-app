import datetime
from contextlib import contextmanager, redirect_stdout
from io import StringIO

import pandas as pd
import streamlit as st

# from ping3 import ping


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


# launch command based on the project
def pipe_cmd(username, selected_pipeline=None, selected_project=None, cmd_num=0, selected_samples="all"):
    if cmd_num == 0:
        path_to_script = get_path_to_script(selected_pipeline, selected_project, selected_samples)
        cmd_pipeline = f"sbatch {path_to_script}"
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


def tab(username, MY_SSH, selected_pipeline, selected_project, selected_samples="all"):
    cols = st.columns([1, 1, 1])
    with cols[0]:
        username = st.text_input(
            "Username(s):",
            username,
            key="username-mod",
            help="Enter your username e.g. ralcraft",
        )

    def run_nextflow():  # username, MY_SSH, selected_pipeline, selected_project):
        cmd_pipeline = pipe_cmd(
            username, selected_pipeline, selected_project, cmd_num=0, selected_samples="all"
        )  # develop this
        st.write("Command used:")
        st.code(cmd_pipeline)
        out_str, err_str = MY_SSH.run_cmd(cmd_pipeline, string=True)

    def check_queue():  # username):
        cmd_pipeline = pipe_cmd(username, None, None, cmd_num=1)
        st.write("Command used:")
        st.code(cmd_pipeline)
        out_str, err_str = MY_SSH.run_cmd(cmd_pipeline, string=True)
        if err_str == "":
            st.write("Output:")
            st.code(out_str)
            st.write(
                "If you see '***' job on compute node, that suggests that the job has been sent to the cluster (in the queue (PD) or running (R))"
            )

        else:
            st.error(err_str)

    left_column, right_column = st.columns(2)
    left_column.button(f"Run the selected nextflow pipeline for {username}", on_click=run_nextflow)
    right_column.button(f"Check queue for {username}", key="checkqueue", on_click=check_queue)
