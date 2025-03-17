import streamlit as st

import tabs.tab_command as tt
from pipeline_project_map import map_pipeline_project
from shared.sessionstate import retrieve_all_from_ss, ss_get, ss_set

# Initialize session state variables
if "select1_value" not in st.session_state:
    ss_set("select1_value", None)
if "select2_value" not in st.session_state:
    ss_set("select2_value", None)


def reset_button_state():
    ss_set("button_clicked", False)


# pull saved values if set, otherwise set to defaults
OK, MY_SSH, username, GROUPS, GROUP, SCRATCH, RDS = retrieve_all_from_ss()

header = """
        <span style=
        "color:darkred;font-size:40px;"> -🍃 </span><span style=
        "color:green;font-size:40px;">RUN NEXTFLOW on ALMA</span><span style=
        "color:darkred;font-size:40px;">🍃- </span>
        """
st.markdown(header, unsafe_allow_html=True)

st.write("---  ")

st.write("## Running Nextflow pipeline on Alma")
st.write("Select your pipeline and your project, then submit the process")

samples = ["all", "demo"]  # , "customised"]
selected_project = None
selected_samples = None

# adding "select" as the first and default choice
selected_pipeline = st.selectbox("Select a pipeline", options=["select"] + list(map_pipeline_project.keys()))
# display selectbox 2 if selected_pipeline is not "select"
if selected_pipeline != "select":
    selected_project = st.selectbox(
        "Select your project",
        options=map_pipeline_project[selected_pipeline],
        on_change=reset_button_state,
        key="select_pipeline",
    )
    selected_samples = st.selectbox("Select your samples", samples, on_change=reset_button_state, key="select_samples")

work_dir = st.text_input("Working directory", SCRATCH)
output_dir = st.text_input("Output directory", RDS)

# passing inputs between tabs
if OK:
    tt.tab(
        username,
        MY_SSH,
        selected_pipeline,
        selected_project,
        selected_samples=selected_samples,
        work_dir=work_dir,
        output_dir=output_dir,
    )
else:
    st.write("#### Log in first to use run nextflow on Alma")
