from subprocess import check_output


class Hostname:
    def __init__(self):
        self.value = check_output(
            ['uname', '-n'],
            universal_newlines=True
        ).rstrip()
