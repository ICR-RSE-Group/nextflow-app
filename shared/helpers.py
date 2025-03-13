from contextlib import contextmanager, redirect_stdout
from io import StringIO

from pyalma import SshClient

############################################################################


# Helper function that streams stdout to a streamlit component
@contextmanager
def st_capture(output_func):
    try:
        with StringIO() as stdout, redirect_stdout(stdout):
            old_write = stdout.write

            def new_write(string):
                ret = old_write(string)
                output_func(stdout.getvalue())
                return True, ret

            stdout.write = new_write
            yield
    except Exception as e:
        return False, e


############################################################################
# Validate user with pyalma library
def validate_user(ssh_host, sftp_host, username, password):
    MY_SSH = SshClient(server=ssh_host, sftp=sftp_host, username=username, password=password)
    print("Validating login...")
    cmd_usr = "sacctmgr list association user=$USER format=Account -P | tail -n +2"
    print("Command:\n", cmd_usr)
    results = MY_SSH.run_cmd(cmd_usr)
    if results["err"] != None:
        print("Errors")
        print(results["err"])
        return False, None, "Correct login details and try again", []
    else:
        groups = results["output"].strip().split("\n")
        return True, MY_SSH, "Session validated successfully", groups


############################################################################
def imply_scratch_rds(username, group):
    if group == "infotech":
        scratch = f"/data/scratch/DCO/DIGOPS/SCIENCOM/{username}"
        rds = "/data/rds/DIT/SCICOM/SCRSE"
    else:
        scratch = f"/scratch/{username}/{group}"
        rds = f"/rds/general/user/{username}/home"
    return scratch, rds
