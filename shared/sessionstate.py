import streamlit as st


def ss_set(key, value):
    st.session_state[key] = value


def ss_get(key, default=""):
    if key in st.session_state:
        return st.session_state[key]
    else:
        return default
