"""GPU information detection class"""

import re

from subprocess import check_output, CalledProcessError

from archey.configuration import Configuration


class GPU:
    """Relies on `lspci` to retrieve graphics device(s) information"""
    def __init__(self):
        # Retrieve a default string from configuration.
        not_detected = Configuration().get('default_strings')['not_detected']

        """
        Some explanations are needed here :
        * We call `lspci` program to retrieve hardware devices
        * We keep only the entries with "3D", "VGA" or "Display"
        * We sort them in the same order as above (for relevancy)
        """
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

                # If the line got too long, let's truncate it and add some dots
                if len(gpuinfo) > 48:
                    # This call truncates `gpuinfo` with words preservation
                    gpuinfo = re.search(
                        r'.{1,45}(?:\s|$)', gpuinfo
                    ).group(0).strip() + '...'

            else:
                gpuinfo = not_detected

        except (FileNotFoundError, CalledProcessError):
            gpuinfo = not_detected

        self.value = gpuinfo
