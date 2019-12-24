"""Hardware model information detection class"""

import os
import re

from subprocess import CalledProcessError, DEVNULL, check_output

from archey.configuration import Configuration


class Model:
    """Uses multiple methods to retrieve some information about the host hardware"""
    def __init__(self):
        self.value = None

        # The configuration object is needed to retrieve some default strings.
        self.default_strings = Configuration().get('default_strings')

        # Is this machine virtualized ?
        self._check_virtualization()

        # Does the OS know something about the hardware ?
        if not self.value:
            self._check_product_name()

        # Is this machine a Raspberry Pi ?
        if not self.value:
            self._check_rasperry_pi()

        if not self.value:
            self.value = self.default_strings['not_detected']

    def _check_virtualization(self):
        """
        Relying on some system tools, tries to gather some details about hypervisor.
        When available, relies on systemd.
        When run as root, `virt-what` and/or `dmidecode` may be called.
        """
        environment, product_name = None, None

        try:
            environment = check_output(
                ['systemd-detect-virt'],
                stderr=DEVNULL, universal_newlines=True
            ).rstrip()
        except (FileNotFoundError, CalledProcessError):
            pass

        # Not a virtualized environment.
        if environment == 'none':
            return

        # When run as root, let's ask `virt-what` and/or `dmidecode`.
        if os.getuid() == 0:
            # We couldn't retrieve any information from `systemd-detect-virt`.
            if not environment:
                try:
                    environment = ', '.join(
                        check_output(
                            ['virt-what'],
                            stderr=DEVNULL, universal_newlines=True
                        ).splitlines()
                    )
                except (FileNotFoundError, CalledProcessError):
                    pass

            try:
                # Sometimes we may gather info added by hosting service provider this way.
                product_name = check_output(
                    ['dmidecode', '-s', 'system-product-name'],
                    stderr=DEVNULL, universal_newlines=True
                ).rstrip()
            except (FileNotFoundError, CalledProcessError):
                pass

        # Definitely not a virtualized environment.
        if not environment:
            return

        # If we reach there, this _should_ be a virtual environment.
        self.value = "{0} ({1})".format(
            product_name or self.default_strings['virtual_environment'],
            environment
        )

    def _check_product_name(self):
        """Tries to open a specific Linux file, looking for machine's product name"""
        try:
            with open('/sys/devices/virtual/dmi/id/product_name') as f_product_name:
                self.value = f_product_name.read().rstrip()
        except FileNotFoundError:
            pass

    def _check_rasperry_pi(self):
        """Tries to retrieve 'Hardware' and 'Revision IDs' from `/proc/cpuinfo`"""
        with open('/proc/cpuinfo') as f_cpu_info:
            cpu_info = f_cpu_info.read()

        # If the output contains 'Hardware' and 'Revision'...
        hardware = re.search('(?<=Hardware\t: ).*', cpu_info)
        revision = re.search('(?<=Revision\t: ).*', cpu_info)
        if hardware and revision:
            # ... let's set a pretty info string with these data
            self.value = 'Raspberry Pi {0} (Rev. {1})'.format(
                hardware.group(0),
                revision.group(0)
            )
