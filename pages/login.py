import streamlit as st

import shared.sessionstate as ss
import tabs.tab_logon as tl

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

st.write("## Login")
st.write("Login to your alma account before running a nextflow pipeline.")

OK, MY_SSH, username = tl.tab()

ss.ss_set("LOGIN_OK", OK)
ss.ss_set("MY_SSH", MY_SSH)
ss.ss_set("user_name", username)


# I want to move between tabs automatically
# move between tabs
def display():
    st.session_state["run_pipeline"] = True
    if st.session_state.get("run_pipeline", False) and "login" in st.session_state:
        if "pages" in st.session_state:
            page = st.session_state["pages"].get("p2", None)
            if page:
                st.switch_page(page)


if "login" not in st.session_state:
    st.session_state["login"] = {}
if "run_pipeline" not in st.session_state:
    st.session_state["run_pipeline"] = False

if OK:
    display()
