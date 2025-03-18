import pandas as pd
import streamlit as st

import tabs.tab_logon as tl
from shared.sessionstate import retrieve_all_from_ss, ss_get, ss_set

header = """
        <span style=
        "color:darkred;font-size:40px;"> -🍃 </span><span style=
        "color:green;font-size:40px;">RUN NEXTFLOW on ALMA</span><span style=
        "color:darkred;font-size:40px;">🍃- </span>
        """
st.markdown(header, unsafe_allow_html=True)

st.write("---  ")

st.write("## Login")
st.write("Login to your alma account before running a nextflow pipeline.")

tl.tab()
# pull saved values if set, otherwise set to defaults
OK, MY_SSH, username, GROUPS, GROUP, SCRATCH, RDS = retrieve_all_from_ss()


# I want to move between tabs automatically
def display():
    # ss_set("run_pipeline", True)
    # if ss_get("run_pipeline", False) and "login" in st.session_state:
    if "pages" in st.session_state:
        page = ss_get("pages").get("p2", None)
        if page:
            st.switch_page(page)


def display_restricted_access(username):
    st.error(
        f"⚠️ Access Restricted ⚠️\n\n"
        f"Dear {username},\n\n"
        "We apologize, but access to the nextflow-app is currently restricted. "
        "For any requests or further information, please contact our support team.\n\n"
        "**Contact Information:**\n"
        "- **Name:** Mira Sarkis\n"
        "- **Department:** Scientific Computing Helpdesk (SCHelpdesk)\n"
        "- **Email:** [schelpdesk@icr.ac.uk](mailto:schelpdesk@icr.ac.uk)\n\n"
        "Thank you for your understanding."
    )

    st.info(
        "ℹ️ **Note:** Please include your username and the reason for your request "
        "when contacting the support team. This will help us process your request more efficiently."
    )


def check_whiteList(username):
    whitelist = "custom_files/user_whitelist.tsv"
    df = pd.read_csv(whitelist, delimiter="\t")
    row = df.loc[df["username"] == username]
    if row.empty:  # user not on the white liste
        return False
    # update session info
    ss_set("user_group", row["group"])
    ss_set("user_cost_account", row["account-code"])
    return True


# if "run_pipeline" not in st.session_state:
#     ss_set("run_pipeline", False)

if OK:
    if not check_whiteList(username):
        display_restricted_access(username)
    else:
        display()
