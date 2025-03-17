from contextlib import contextmanager, redirect_stdout
from io import StringIO

import yaml
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
        err_msg = "Connection failed: " + results["err"]
        return False, None, err_msg, []
    else:
        groups = results["output"].strip().split("\n")[1:]
        return True, MY_SSH, "Session validated successfully", groups


############################################################################
def get_scratch_rds_path(username, group, yaml_file="custom_files/group_path_map.yaml"):
    print(username, group)
    with open(yaml_file, "r") as file:
        config = yaml.safe_load(file)

    group_config = config["group_paths"].get(group, config["group_paths"].get("default"))

    scratch = group_config["scratch"].format(username=username, group=group)
    rds = group_config["rds"].format(username=username)
    print(scratch, rds)
    return scratch, rds
