import paramiko


def make_sftp_client(host, credentials, *args, **kwargs):
    port = kwargs.get('port', 22)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, *credentials, *args, **kwargs)

    sftp = ssh.open_sftp()

    return sftp
