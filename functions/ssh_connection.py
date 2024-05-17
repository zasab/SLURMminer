import paramiko
import pysftp

class My_Connection(pysftp.Connection):
    def __init__(self, *args, **kwargs):
        self._sftp_live = False
        self._transport = None
        super().__init__(*args, **kwargs)

def get_ssh_client2(server, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=username, password=password)
    return ssh


def get_ssh_client(hostname, username, password, two_factor_code_filepath):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("two_factor_code_filepath: ", two_factor_code_filepath)
        ssh.connect(hostname, username=username, password=password, key_filename=two_factor_code_filepath)
        return ssh
    except paramiko.AuthenticationException as e:
        print("Authentication failed:", e)
        return None