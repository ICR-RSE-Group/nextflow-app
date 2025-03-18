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
    keys_defaults = {
        "LOGIN_OK": False,
        "MY_SSH": None,
        "user_name": "",
        "GROUPS": "",
        "GROUP": "Select an option",
        "SCRATCH": "",
        "RDS": "",
        "PROJECT": None,
        "SAMPLE": None,
        "PIPELINE": "select",
    }

    return tuple(ss_get(key, default) for key, default in keys_defaults.items())
