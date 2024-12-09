import streamlit as st

import shared.sessionstate as ss
import tabs.tab_command as tt

header = """
        <span style="color:black;">
        <img src="https://www.icr.ac.uk/assets/img/logo.png"
        alt="icr" width="200px"></span><span style=
        "color:darkred;font-size:40px;"> -🍃 </span><span style=
        "color:green;font-size:40px;">RUN-NEXTFLOW</span><span style=
        "color:darkred;font-size:40px;">🍃- </span>
        """
st.markdown(header, unsafe_allow_html=True)

st.write("---  ")

st.write("## Running Nextflow pipeline on Alma")
st.write("Select your pipeline and your project, then submit the process")

LOGIN_OK = ss.ss_get("LOGIN_OK")
MY_SSH = ss.ss_get("MY_SSH")
username = ss.ss_get("user_name")

pipelines = ["epi2me-human-variation", "epi2me-somatic-variation", "nfcore-rnaseq"]
projects = ["nf-long-reads", "nf-tp53", "mopopgen-support"]
samples = ["all", "demo"]  # , "customised"]

map_pipeline_project = {
    "epi2me-human-variation": ["nf-long-reads"],
    "epi2me-somatic-variation": ["nf-tp53"],
    "nfcore-rnaseq": ["mopopgen-support"],
}
selected_project = None
selected_samples = None
# adding "select" as the first and default choice
selected_pipeline = st.selectbox("Select a pipeline", options=["select"] + list(map_pipeline_project.keys()))
# display selectbox 2 if selected_pipeline is not "select"
if selected_pipeline != "select":
    selected_project = st.selectbox("Select your project", options=map_pipeline_project[selected_pipeline])
    selected_samples = st.selectbox("Select your samples", samples)

# passing inputs between tabs
if LOGIN_OK:
    tt.tab(username, MY_SSH, selected_pipeline, selected_project, selected_samples)
else:
    st.write("#### To use run nextflow on Alma, please log in first")
