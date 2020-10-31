"""Local IP addresses detection class"""

import ipaddress
import sys

from itertools import islice

try:
    import netifaces
except ImportError:
    netifaces = None

from archey.entry import Entry


class LanIP(Entry):
    """Relies on the `netifaces` module to detect LAN IP addresses"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not netifaces:
            print(
                """\
Warning: `netifaces` Python module couldn\'t be found.
Please either install it or disable `LAN_IP` entry in configuration.\
""",
                file=sys.stderr
            )
            return

        # IPv4 will be enabled by default.
        addr_families = [netifaces.AF_INET]
        if self.options.get('ipv6_support', True):
            addr_families.append(netifaces.AF_INET6)

        max_count = self.options.get('max_count', 2)
        # Consistency with other entries' configuration: Infinite count if false.
        if max_count is False:
            max_count = None

        self.value = list(
            islice(self._lan_ip_addresses_generator(addr_families), max_count)
        )

    @staticmethod
    def _lan_ip_addresses_generator(addr_families):
        """Generator yielding local IP address according to passed address families"""
        # Loop through all available network interfaces.
        for if_name in netifaces.interfaces():
            # Fetch associated addresses elements.
            if_addrs = netifaces.ifaddresses(if_name)

            for addr_family in addr_families:
                for if_addr in if_addrs.get(addr_family, []):
                    # IPv6 addresses may contain '%' token separator.
                    ip_addr = ipaddress.ip_address(if_addr['addr'].split('%')[0])

                    # Filter out loopback addresses.
                    if not ip_addr.is_loopback:
                        # Finally, yield the address compressed representation.
                        yield ip_addr.compressed


    def output(self, output):
        """Adds the entry to `output` after pretty-formatting the IP address list."""
        # If we found IP addresses, join them together nicely.
        # If not, fall back on default strings according to `netifaces` availability.
        if self.value:
            text_output = ', '.join(self.value)
        elif netifaces:
            text_output = self._default_strings.get('no_address')
        else:
            text_output = self._default_strings.get('not_detected')

        output.append(self.name, text_output)
