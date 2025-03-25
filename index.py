import streamlit as st

st.set_page_config(
    page_icon="🍃",
    page_title="run-nextflow on Alma",
    layout="wide",
    initial_sidebar_state="auto",
)
# redirect directly to login page
st.switch_page("pages/login.py")
