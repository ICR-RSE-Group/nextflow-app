from contextlib import contextmanager, redirect_stdout
from io import StringIO

import streamlit as st
from pyalma import LocalFileReader, SshClient


@contextmanager
def st_capture(output_func):
    try:
        with StringIO() as stdout, redirect_stdout(stdout):
            old_write = stdout.write

            def new_write(string):
                ret = old_write(string)
                output_func(stdout.getvalue())
                return ret

            stdout.write = new_write
            yield
    except Exception as e:
        st.error(str(e))


def tab():
    MY_SSH = None
    OK = False

    cols = st.columns(3)
    with cols[0]:
        server = st.text_input("Enter your remote server:", "alma.icr.ac.uk")
    with cols[1]:
        username = st.text_input("Enter your username:", key="username")
    with cols[2]:
        password = st.text_input("Enter your password:", "", type="password", key="password")

    if st.button("Connect", key="connect"):
        if username == "admin" and password == "admin":
            st.success("Admin login successful")
            OK = True
        else:
            with st.spinner("Validating login"):
                MY_SSH = SshClient(server, username, password)
                print("Validating login...")

                _dict = MY_SSH.run_cmd("cd ~ &ls -l")
                OK = _dict["err"] is None
                if OK:
                    print("Session validated successfully")
                    st.success("Session validated successfully")
                else:
                    print("Errors", _dict["err"])
                    err_msg = "Connection failed: " + _dict["err"]
                    st.error(err_msg)

    return OK, MY_SSH, username
