import os
import sys

import pandas as pd
import paramiko

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
__file__


class SshConnection:
    def __init__(self, source, username, password, server="alma.icr.ac.uk"):
        self.source = source.strip()
        self.server = server.strip()
        self.username = username.strip()
        self.password = password.strip()

    def run_cmd(self, cmd, string=True):
        if self.source == "local":
            return self.run_local(cmd)
        else:
            try:
                with paramiko.SSHClient() as client:
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(self.server, username=self.username, password=self.password)
                    stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
                    err_str = stderr.read().decode("ascii")

                    if string:
                        out_str = stdout.read().decode("ascii")
                        return out_str, err_str

                    else:
                        from io import BytesIO

                        df = pd.read_csv(BytesIO(stdout.read()), sep="|")
                        return df, err_str

            except Exception as e:
                return "", str(e)