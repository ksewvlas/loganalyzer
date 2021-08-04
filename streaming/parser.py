import re

DEFAULT = '$remote_addr - $remote_user [$time_local] "$request" ' \
          '$status $body_bytes_sent "$http_referer" "$http_user_agent"'


class NginxLogsParser:
    def __init__(self, nginx_log_pattern=DEFAULT):
        self.pattern = nginx_log_pattern
        self.regexp = self._make_regexp(nginx_log_pattern)

    @staticmethod
    def _make_regexp(nginx_log_pattern):
        return ''.join(
            '(?P<' + g + '>.*?)' if g else re.escape(c)
            for g, c in re.findall(r'\$(\w+)|(.)', nginx_log_pattern)
        )

    def parse(self, line):
        data = re.search(self.regexp, line)

        if data:
            return data.groupdict()
