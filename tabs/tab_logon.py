import streamlit as st

import shared.helpers as hlp
from shared.sessionstate import retrieve_all_from_ss, save_in_ss, ss_get, ss_set


def handle_login(server, sftp_server, username, password):
    if username == "admin" and password == "admin":
        st.success("Admin login successful")
        return True, None, "Admin login successful", None  # No SSH or groups needed for admin

    with st.spinner("Validating login..."):
        OK, MY_SSH, msg, GROUPS = hlp.validate_user(server, sftp_server, username, password)

    return OK, MY_SSH, msg, GROUPS


# once connected, you cannot try to re-connect
def tab():
    # pull saved values if set, otherwise set to defaults
    keys = ["LOGIN_OK", "MY_SSH", "user_name", "GROUPS", "GROUP", "SCRATCH", "RDS", "PROJECT", "SAMPLE"]
    (OK, MY_SSH, username, GROUPS, GROUP, SCRATCH, RDS, PROJECT, SAMPLE, PIPELINE) = retrieve_all_from_ss()
    cols = st.columns(3)
    with cols[0]:
        server = st.text_input("Enter your remote server:", "alma.icr.ac.uk", key="server")
    with cols[1]:
        username = st.text_input("Enter your username:", key="username")
    with cols[2]:
        password = st.text_input("Enter your password:", "", type="password", key="password")
    sftp_server = "alma-app.icr.ac.uk"

    def update_group():
        GROUP = ss_get("group_selection")
        SCRATCH, RDS = hlp.get_scratch_rds_path(username, GROUP)
        save_in_ss(
            {
                "LOGIN_OK": True,
                "MY_SSH": MY_SSH,
                "user_name": username,
                "GROUPS": GROUPS,
                "GROUP": GROUP,
                "SCRATCH": SCRATCH,
                "RDS": RDS,
            }
        )

    def handle_group_selection(GROUPS):
        st.radio(
            "Select group",
            ["Select an option"] + GROUPS,
            horizontal=True,
            index=0,
            key="group_selection",
            on_change=update_group,
        )
        return

    if st.button("Connect", key="connect"):
        OK, MY_SSH, msg, GROUPS = handle_login(server, sftp_server, username, password)
        if OK:
            st.success(msg)
            handle_group_selection(GROUPS)
        else:
            st.error(msg)

    return
