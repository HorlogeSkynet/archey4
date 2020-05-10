"""GPU information detection class"""

from subprocess import check_output, CalledProcessError

from archey.entry import Entry


class GPU(Entry):
    """Relies on `lspci` to retrieve graphical device(s) information"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # This list will contain GPU devices detected on this system.
        self.gpu_devices = []

        # Let's try to run `lspci` and parse here.
        self._run_lspci()

        self.value = ', '.join(self.gpu_devices) or \
            self._configuration.get('default_strings')['not_detected']

    def _run_lspci(self):
        """Based on `lspci` output, retrieve a list of video controllers names"""
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
                    # ... adds its name to our final list.
                    self.gpu_devices.append(pci_device.partition(': ')[2])
