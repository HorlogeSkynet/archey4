"""Host name detection class"""

from subprocess import check_output

from archey.entry import Entry


class Hostname(Entry):
    """Simple call to `uname` to retrieve the host name"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = self._read_etc_hostname()
        if not self.value:
            self.value = check_output(
                ['uname', '-n'],
                universal_newlines=True
            ).rstrip()

    @staticmethod
    def _read_etc_hostname():
        try:
            with open('/etc/hostname') as f_hostname:
                return f_hostname.read().rstrip()
        except FileNotFoundError:
            return None
