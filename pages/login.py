import pandas as pd
import streamlit as st

import tabs.tab_logon as tl
from shared.sessionstate import retrieve_all_from_ss, ss_set
from shared.visual import header

st.title("🔑 Login Page")

header()
st.write("## Login")
st.write("Login to your alma account before running a nextflow pipeline.")

tl.tab()

ss_values = retrieve_all_from_ss()
OK = ss_values["OK"]
username = ss_values["user_name"]
GROUP = ss_values["GROUP"]


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
    if row.empty:  # user not on the white list
        return False
    # update session info
    ss_set("user_group", row["group"])
    ss_set("user_cost_account", row["account-code"])
    return True


if OK and GROUP != "":
    if not check_whiteList(username):
        display_restricted_access(username)
