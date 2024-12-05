import shared.sessionstate as ss
import streamlit as st
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
st.write(
    "Select your pipeline and your project, then submit the process"
)

LOGIN_OK = ss.ss_get("LOGIN_OK")
MY_SSH = ss.ss_get("MY_SSH")
username = ss.ss_get("user_name")

# Algorithm and project selection --> we should rename 
pipelines = ["nf-human-variation"]#, "nf-somatic-variation", "rnaseq"]
projects = ["nf-long-reads"]#, "nf-tp53"]

selected_pipeline = st.selectbox("Select a pipeline", pipelines)
selected_project = st.selectbox("Select your project", projects)

#passing inputs between tabs
if LOGIN_OK:
    tt.tab(username, MY_SSH, selected_pipeline, selected_project)
else:
    st.write("#### To use run nextflow on Alma, please log in first")