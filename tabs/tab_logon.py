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
    group_selection = ss_values["group_selection"]

    cols = st.columns(3)
    with cols[0]:
        server = st.text_input("Enter your remote server:", value=server)
    with cols[1]:
        username = st.text_input("Enter your username:", key="username", value=username)
    with cols[2]:
        password = st.text_input("Enter your password:", type="password", value=password)
    sftp_server = "alma-app.icr.ac.uk"

    # Temporary session key for updating selection
    if "temp_group_selection" not in st.session_state:
        ss_set("temp_group_selection", ss_get("group_selection", "Select an option"))
        st.write(ss_get("temp_group_selection"))

    def update_group():
        ss_set("group_selection", st.session_state["temp_group_selection"])
        st.write(ss_get("group_selection"))
        SCRATCH, RDS = hlp.get_scratch_rds_path(username, st.session_state["group_selection"])
        save_in_ss(
            {
                "OK": True,
                "MY_SSH": MY_SSH,
                "user_name": username,
                "GROUPS": GROUPS,
                "GROUP": ss_get("group_selection"),
                "SCRATCH": SCRATCH,
                "RDS": RDS,
            }
        )

    def create_radio(GROUPS):
        options = ["Select an option"] + GROUPS if GROUPS else ["Select an option"]

        st.radio(
            "Select group",
            options,
            index=options.index(ss_get("group_selection")),
            key="temp_group_selection",  # Temporary key for updates
            on_change=update_group,  # Calls update function on change
        )

    # Handle connection
    if st.button("Connect", key="connect"):
        OK, MY_SSH, msg, GROUPS = handle_login(server, sftp_server, username, password)
        if OK:
            st.success(msg)
        else:
            st.error(msg)

    # Ensure radio button persists after connection
    if "GROUPS" in locals() and GROUPS:
        create_radio(GROUPS)

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
            "JOB_ID": JOB_ID,
            "group_selection": GROUP,
        }
    )
