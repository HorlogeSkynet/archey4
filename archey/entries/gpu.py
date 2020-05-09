"""GPU information detection class"""

from subprocess import check_output, CalledProcessError

from archey.entry import Entry


class GPU(Entry):
    """Relies on `lspci` to retrieve graphics device(s) information"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # This list will contain GPU devices detected on this system.
        self.gpu_devices = []

        # Let's try `lspci` here.
        self._run_lspci()

        self.value = ', '.join(self.gpu_devices) or \
            self._configuration.get('default_strings')['not_detected']

    def _run_lspci(self):
        """Based on `lspci` output, retrieve a list of GPU devices"""
        # Let's ask `lspci` for a list of current PCI devices on this system.
        try:
            lspci_output = check_output(
                ['lspci'],
                universal_newlines=True
            ).splitlines()
        except (FileNotFoundError, CalledProcessError):
            return

        # Prepares a list of video-only controllers (weighted by the below keys).
        for video_key in ('3D', 'VGA', 'Display'):
            for pci_device in lspci_output:
                if video_key in pci_device:
                    self.gpu_devices.append(pci_device.partition(': ')[2])
