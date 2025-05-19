import streamlit as st

import tabs.tab_command as tt
from pipeline_project_map import map_pipeline_project
from shared.sessionstate import retrieve_all_from_ss, save_in_ss, ss_get, ss_set
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
WORK_DIR = ss_values["WORK_DIR"]
OUTPUT_DIR = ss_values["OUTPUT_DIR"]
run_pipeline_clicked = ss_values["run_pipeline_clicked"]
button_clicked = ss_values["button_clicked"]
custom_sample_list = ss_values["custom_sample_list"]  # only availanle if custom sample is selected
BED_FILE = ss_values["BED_FILE"]
samples = ["demo", "customised"]  # , "test"]

# Create the selectbox and update session state
pipeline_options = ["select"] + list(map_pipeline_project.keys())
index = pipeline_options.index(PIPELINE)
PIPELINE = st.selectbox("Select a pipeline", options=pipeline_options, index=index)
adapt_samples = False
# adding "select" as the first and default choice
if PIPELINE != "select":
    project_options = list(map_pipeline_project[PIPELINE].keys())

    PROJECT = st.selectbox(
        "Select your project",
        options=project_options,
        index=project_options.index(PIPELINE) if PIPELINE in project_options else 0,
        on_change=reset_button_state,
    )
    # samples here depend on the pipeline: human variation requires bam files, rnaseq requires a samplesheet
    SAMPLE = st.selectbox(
        "Select your samples",
        options=samples,
        index=samples.index(SAMPLE) if SAMPLE in samples else 0,
        on_change=reset_button_state,
    )

    # If "customised" is selected, show additional input
    if SAMPLE == "customised":
        is_input_type_path = map_pipeline_project[PIPELINE][PROJECT]["is_inputType_path"]
        msg = "Enter your sample names (comma-separated)"
        if is_input_type_path:
            msg = "Enter path to samplesheet"
        custom_samples = st.text_input(msg, key="custom_samples", value=",".join(custom_sample_list))

        # Optionally process the input into a list
        if custom_samples:
            custom_sample_list = [s.strip() for s in custom_samples.split(",") if s.strip()]

            st.write("Your custom samples:", custom_sample_list)
            ss_set("custom_sample_list", custom_sample_list)
    
    if(map_pipeline_project[PIPELINE][PROJECT]["adapt_samples"]):
        adapt_samples = st.checkbox("Adapt samples prior to running nextflow", 
                            value=False,
                            help="If you are not sure, check if your samples are available in /data/rds/DGE/DUDGE/OGENETIC/Data/Nanopore/samples"
                            )

    use_bed_file = map_pipeline_project[PIPELINE][PROJECT]["bed_file_as_arg"]#bool
    # Optional BED file path
    BED_FILE = st.text_input(
        "Optional BED file path",
        value="",
        help="Provide a full path to a BED file on Alma server, or leave empty to skip and use full genome",
        disabled=not use_bed_file
    )
WORK_DIR = st.text_input("Working directory", value=WORK_DIR or SCRATCH)
OUTPUT_DIR = st.text_input("Output directory", value=OUTPUT_DIR or SCRATCH)
dry_run = st.checkbox("Dry run (do not execute the job)", value=False)

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
        custom_sample_list=custom_sample_list,
        bed_file=BED_FILE,
        dry_run=dry_run,
        adapt_samples=adapt_samples
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
            # "JOB_ID": JOB_ID,
            "WORK_DIR": WORK_DIR,
            "OUTPUT_DIR": OUTPUT_DIR,
            "run_pipeline_clicked": run_pipeline_clicked,
            "button_clicked": button_clicked,
            "custom_sample_list": custom_sample_list,
            "BED_FILE":BED_FILE,
        }
    )
else:
    st.write("#### Log in first to use run nextflow on Alma")
