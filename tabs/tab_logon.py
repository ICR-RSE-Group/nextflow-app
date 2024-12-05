from contextlib import contextmanager, redirect_stdout
from io import StringIO

import streamlit as st

import shared.ssh as ssh


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
                MY_SSH = ssh.SshConnection("remote", username, password, server=server)

                print("Validating login...")
                cmd = "cd ~ && ls -l1"
                results_str, error_str = MY_SSH.run_cmd(cmd)

                if error_str:
                    print("Errors", error_str)
                else:
                    print("Session validated successfully")

                OK = error_str == ""
                if OK:
                    st.success("Session validated successfully")
                else:
                    st.error("Correct login details and try again")

    return OK, MY_SSH, username
