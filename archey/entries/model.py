"""Hardware model information detection class"""

import re

from subprocess import CalledProcessError, DEVNULL, check_output

from archey.configuration import Configuration


class Model:
    """Uses multiple methods to retrieve some information about the host hardware"""
    def __init__(self):
        try:
            with open('/sys/devices/virtual/dmi/id/product_name') as file:
                model = file.read().rstrip()

        except FileNotFoundError:
            # The file above does not exist, is this device a Raspberry Pi ?
            # Let's retrieve the Hardware and Revision IDs with `/proc/cpuinfo`
            with open('/proc/cpuinfo') as file:
                output = file.read()

            hardware = re.search('(?<=Hardware\t: ).*', output)
            revision = re.search('(?<=Revision\t: ).*', output)

            # If the output contains 'Hardware' and 'Revision'...
            if hardware and revision:
                # ... let's set a pretty info string with these data
                model = 'Raspberry Pi {0} (Rev. {1})'.format(
                    hardware.group(0),
                    revision.group(0)
                )

            else:
                # The configuration object is needed to retrieve some settings below.
                configuration = Configuration()

                # A tricky way to retrieve some details about hypervisor...
                # ... within virtual contexts.
                # `archey` needs to be run as root although.
                try:
                    virt_what = ', '.join(
                        check_output(
                            ['virt-what'],
                            stderr=DEVNULL, universal_newlines=True
                        ).splitlines()
                    )

                    if virt_what:
                        try:
                            # Sometimes we may gather info added by...
                            # ... hosting service provider this way
                            model = check_output(
                                ['dmidecode', '-s', 'system-product-name'],
                                stderr=DEVNULL, universal_newlines=True
                            ).rstrip()

                        except (FileNotFoundError, CalledProcessError):
                            model = configuration.get('default_strings')['virtual_environment']

                        model += ' ({0})'.format(virt_what)

                    else:
                        model = configuration.get('default_strings')['bare_metal_environment']

                except (FileNotFoundError, CalledProcessError):
                    model = configuration.get('default_strings')['not_detected']

        self.value = model
