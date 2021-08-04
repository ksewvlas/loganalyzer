import os
import abc
import gzip
import time

from paramiko import SFTPClient

from streaming.parser import NginxLogsParser


class RemoteLogReader(abc.ABC):
    STARTS_WITH_FILE = None

    def __init__(self, sftp: SFTPClient, log_path: str, **kwargs):
        self._sftp = sftp
        self._log_path = log_path

        log_format = kwargs['log_format']

        self.parser = NginxLogsParser(log_format)

    def read(self, file='access.log'):
        path = os.path.join(self._log_path, file)

        logfile = self._sftp.open(path)

        if file.endswith('.gz'):
            logfile = gzip.GzipFile(mode='rb', fileobj=logfile)

        logfile.seek(0, 2)

        while True:
            line = logfile.readline()
            if not line:
                time.sleep(0.01)

                continue

            yield self.parser.parse(line)


class RemoteNginxAccessReader(RemoteLogReader):
    STARTS_WITH_FILE = 'access'
