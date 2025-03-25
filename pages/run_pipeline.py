import streamlit as st

import tabs.tab_command as tt
from pipeline_project_map import map_pipeline_project
from shared.sessionstate import retrieve_all_from_ss, save_in_ss, ss_set
from shared.visual import header


def reset_button_state():
    ss_set("button_clicked", False)


header()
st.write("## Running Nextflow pipeline on Alma")
st.write("Select your pipeline and your project, then submit the process")

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
button_clicked = ss_values["button_clicked"]

samples = ["all", "demo"]  # , "customised"]

# Create the selectbox and update session state
options = ["select"] + list(map_pipeline_project.keys())
index = options.index(PIPELINE)
PIPELINE = st.selectbox("Select a pipeline", options=options, index=index)  # , key="PIPELINE")
# adding "select" as the first and default choice
if PIPELINE != "select":
    PROJECT = st.selectbox(
        "Select your project",
        options=map_pipeline_project[PIPELINE],
        index=map_pipeline_project[PIPELINE].index(PIPELINE) if PIPELINE in map_pipeline_project[PIPELINE] else 0,
        on_change=reset_button_state,
    )

    SAMPLE = st.selectbox(
        "Select your samples",
        options=samples,
        index=samples.index(SAMPLE) if SAMPLE in samples else 0,
        on_change=reset_button_state,
    )

WORK_DIR = st.text_input("Working directory", value=SCRATCH)
OUTPUT_DIR = st.text_input("Output directory", value=SCRATCH)

# passing inputs between tabs
if OK:
    tt.tab(
        username,
        MY_SSH,
        PIPELINE,
        PROJECT,
        selected_samples=SAMPLE,
        work_dir=WORK_DIR,
        output_dir=OUTPUT_DIR,
    )
    save_in_ss(
        {
            "OK": OK,
            "MY_SSH": MY_SSH,
            "user_name": username,
            "server": server,
            "password": password,
            "GROUP": GROUP,
            "GROUPS": GROUPS,
            "SCRATCH": SCRATCH,
            "RDS": RDS,
            "SAMPLE": SAMPLE,
            "PIPELINE": PIPELINE,
            "PROJECT": PROJECT,
            "JOB_ID": JOB_ID,
            "WORKDIR": WORK_DIR,
            "OUTPUT_DIR": OUTPUT_DIR,
            "run_pipeline_clicked": run_pipeline_clicked,
            "button_clicked": button_clicked,
        }
    )
else:
    st.write("#### Log in first to use run nextflow on Alma")
