import streamlit as st

import shared.helpers as hlp
from shared.sessionstate import retrieve_all_from_ss, save_in_ss, ss_get


# once connected, you cannot try to re-connect
def tab():
    # pull saved values if set, otherwise set to defaults
    keys = ["LOGIN_OK", "MY_SSH", "user_name", "GROUPS", "GROUP", "SCRATCH", "RDS", "PROJECT", "SAMPLE"]
    OK, MY_SSH, username, GROUPS, GROUP, SCRATCH, RDS, PROJECT, SAMPLE, PIPELINE = retrieve_all_from_ss()
    cols = st.columns(3)
    with cols[0]:
        server = st.text_input("Enter your remote server:", "alma.icr.ac.uk", key="server")
    with cols[1]:
        username = st.text_input("Enter your username:", key="username")
    with cols[2]:
        password = st.text_input("Enter your password:", "", type="password", key="password")
    sftp_server = "alma-app.icr.ac.uk"
    if st.button("Connect", key="connect"):
        if username == "admin" and password == "admin":
            st.success("Admin login successful")
            OK = True
        else:
            with st.spinner("Validating login"):
                OK, MY_SSH, msg, GROUPS = hlp.validate_user(server, sftp_server, username, password)
                print(OK, MY_SSH, msg, GROUPS)
                if OK:
                    st.success(msg)
                    GROUP = st.radio("Select group", GROUPS, horizontal=True)
                    SCRATCH, RDS = hlp.get_scratch_rds_path(username, GROUP)
                    # save in session states
                    ss_dict = {
                        "LOGIN_OK": OK,
                        "MY_SSH": MY_SSH,
                        "user_name": username,
                        "GROUPS": GROUPS,
                        "GROUP": GROUP,
                        "SCRATCH": SCRATCH,
                        "RDS": RDS,
                    }
                    save_in_ss(ss_dict)
                else:
                    st.error(msg)

    return OK, MY_SSH, username
