import os

import streamlit as st
import yaml


def ss_set(key, value):
    st.session_state[key] = value


def ss_get(key, default="todrop"):
    if key in st.session_state:
        return st.session_state[key]
    else:
        # we should update it to read from ss_defaults
        return keys_defaults[key]


def save_in_ss(data_dict):
    for key, value in data_dict.items():
        ss_set(key, value)


def load_defaults_from_yaml():
    file_path = "ss_defaults.yaml"
    file_path = os.path.join(os.path.dirname(__file__), file_path)
    try:
        with open(file_path, "r") as file:
            defaults = yaml.safe_load(file)
            return defaults.get("keys_defaults", {})
    except Exception as e:
        print(f"Error loading YAML: {e}")
        return {}


def retrieve_all_from_ss():
    return {key: ss_get(key, default) for key, default in keys_defaults.items()}


def list_all():
    # for key, value in st.session_state.items():
    #     st.write(f"🔹 **{key}**: {value}")
    st.json(st.session_state.to_dict())


keys_defaults = load_defaults_from_yaml()
