"""GPU information detection class"""

from subprocess import CalledProcessError, check_output
from itertools import islice

from archey.entry import Entry


class GPU(Entry):
    """Relies on `lspci` to retrieve graphical device(s) information"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        max_count = self._configuration.get('gpu')['max_count']
        # Consistency with other entries' configuration: Infinite count if false.
        if max_count is False:
            max_count = None

        # Populate our list of devices with the `lspci`-based generator.
        self.value = list(islice(self._gpu_generator(), max_count))

    @staticmethod
    def _gpu_generator():
        """Based on `lspci` output, return a generator for video controllers names"""
        try:
            lspci_output = check_output(
                ['lspci'],
                universal_newlines=True
            ).splitlines()
        except (FileNotFoundError, CalledProcessError):
            return

        # We'll be looking for specific video controllers (in the below keys order).
        for video_key in ('3D', 'VGA', 'Display'):
            for pci_device in lspci_output:
                # If a controller type match...
                if video_key in pci_device:
                    # ... return its name on the next iteration.
                    yield pci_device.partition(': ')[2]


    def output(self, output):
        """Writes GPUs to `output` based on preferences"""
        # Even when no GPU device could be detected, be sure to add an "empty" entry to `output`.
        if self._configuration.get('gpu')['one_line'] or not self.value:
            output.append(
                self.name,
                ', '.join(self.value) or self._configuration.get('default_strings')['not_detected']
            )
        else:
            for gpu_device in self.value:
                output.append(self.name, gpu_device)
