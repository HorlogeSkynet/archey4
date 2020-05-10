"""GPU information detection class"""

from itertools import islice
from subprocess import check_output, CalledProcessError

from archey.entry import Entry


class GPU(Entry):
    """Relies on `lspci` to retrieve graphical device(s) information"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._max_count = self._configuration.get('gpu').get('max_count', None)
        # Consistency with other entries' configuration: Infinite count if false.
        if self._max_count is False:
            self._max_count = None

        # Populate our list of devices with the `lspci`-based generator.
        self.gpu_devices = list(islice(self._gpu_generator(), self._max_count))


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
        """Writes GPUs to `output` based on preferences."""
        if self.gpu_devices:
            if self._configuration.get('gpu').get('one_line', False):
                output.append(self.name, ', '.join(self.gpu_devices))
            else:
                for gpu in self.gpu_devices:
                    output.append(self.name, gpu)
        else:
            output.append(self.name, self._configuration.get('default_strings')['not_detected'])
