"""GPU information detection class"""

from subprocess import check_output, CalledProcessError

from archey.entry import Entry


class GPU(Entry):
    """Relies on `lspci` to retrieve graphics device(s) information"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        gpuinfo = None

        # Some explanations are needed here :
        # * We call `lspci` program to retrieve hardware devices
        # * We keep only the entries with "3D", "VGA" or "Display"
        # * We sort them in the same order as above (for relevancy)
        try:
            lspci_output = sorted(
                [
                    i.split(': ')[1] for i in check_output(
                        ['lspci'], universal_newlines=True
                    ).splitlines()
                    if '3D' in i or 'VGA' in i or 'Display' in i
                ], key=len
            )

            if lspci_output:
                gpuinfo = lspci_output[0]

        except (FileNotFoundError, CalledProcessError):
            pass

        self.value = gpuinfo
