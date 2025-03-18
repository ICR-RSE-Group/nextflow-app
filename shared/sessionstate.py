import streamlit as st


def ss_set(key, value):
    st.session_state[key] = value


def ss_get(key, default=""):
    if key in st.session_state:
        return st.session_state[key]
    else:
        return default


# I would definitely replace below exhaustive list with dictionaries
def save_in_ss(data_dict):
    for key, value in data_dict.items():
        ss_set(key, value)


def retrieve_all_from_ss():
    OK = ss_get("LOGIN_OK", False)
    MY_SSH = ss_get("MY_SSH", None)
    username = ss_get("user_name", "")
    GROUPS = ss_get("GROUPS", "")
    GROUP = ss_get("GROUP", "")
    SCRATCH = ss_get("SCRATCH", "")
    RDS = ss_get("RDS", "")
    PROJECT = ss_get("PROJECT", None)
    SAMPLE = ss_get("SAMPLE", None)
    PIPELINE = ss_get("PIPELINE", "select")
    return OK, MY_SSH, username, GROUPS, GROUP, SCRATCH, RDS, PROJECT, SAMPLE, PIPELINE


#    keys = ["LOGIN_OK", "MY_SSH", "user_name", "GROUPS", "GROUP", "SCRATCH", "RDS"]
# def retrieve_all_from_ss(keys):
#     return {key: ss_get(key, default_value) for key, default_value in zip(keys, [False, None, "", "", "", "", ""])}
