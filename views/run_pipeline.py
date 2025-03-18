import streamlit as st

import tabs.tab_command as tt
from pipeline_project_map import map_pipeline_project
from shared.sessionstate import retrieve_all_from_ss, ss_get, ss_set
from shared.visual import header


def reset_button_state():
    ss_set("button_clicked", False)


header()
st.write("## Running Nextflow pipeline on Alma")
st.write("Select your pipeline and your project, then submit the process")

# pull saved values if set, otherwise set to defaults
(OK, MY_SSH, username, GROUPS, GROUP, SCRATCH, RDS, PROJECT, SAMPLE, PIPELINE) = retrieve_all_from_ss()

samples = ["all", "demo"]  # , "customised"]

# Create the selectbox and update session state
options = ["select"] + list(map_pipeline_project.keys())
index = options.index(PIPELINE)
PIPELINE = st.selectbox("Select a pipeline", options=options, index=index, key="PIPELINE")
# adding "select" as the first and default choice
if PIPELINE != "select":
    PROJECT = st.selectbox(
        "Select your project",
        options=map_pipeline_project[PIPELINE],
        index=map_pipeline_project[PIPELINE].index(PIPELINE) if PIPELINE in map_pipeline_project[PIPELINE] else 0,
        key="PROJECT",
        on_change=reset_button_state,
    )

    SAMPLE = st.selectbox(
        "Select your samples",
        options=samples,
        index=samples.index(SAMPLE) if SAMPLE in samples else 0,
        key="SAMPLE",
        on_change=reset_button_state,
    )

WORK_DIR = st.text_input("Working directory", value=SCRATCH, key="WORK_DIR")
OUTPUT_DIR = st.text_input("Output directory", value=SCRATCH, key="OUTPUT_DIR")

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
else:
    st.write("#### Log in first to use run nextflow on Alma")
