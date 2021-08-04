import threading

from db import create_alchemy_engine
from streaming.reader import RemoteNginxAccessReader
from streaming.sftp import make_sftp_client
from streaming.queries import add_log, get_settings_by_pid


class SFTPAccessLogStreaming(threading.Thread):
    def __init__(self, config, project_id, *args, **kwargs):
        pid = str(project_id)

        super(SFTPAccessLogStreaming, self).__init__(name=pid, *args, **kwargs)

        self._config = config
        self._db_engine = create_alchemy_engine(self._config['postgres'])
        self._conn = self._db_engine.connect()

        self.pid = pid

        self._settings = get_settings_by_pid(self._conn, pid)

        ssh_setts = self._settings['ssh']

        self._sftp = make_sftp_client(
            host=ssh_setts['host'],
            credentials=(ssh_setts['user'], ssh_setts['password']),
        )

        self._reader = RemoteNginxAccessReader(
            self._sftp,
            self._settings['access_log_path'],
            log_format=self._settings['access_log_format'],
        )

        self._stop = False

    def run(self) -> None:
        for log in self._reader.read():
            if self._stop:
                break

            add_log(self._db_engine, self.pid, log)

    def stop(self):
        self._stop = True

    @property
    async def stopped(self):
        return self._stop
