"""Local IP addresses detection class"""

import sys

try:
    import netifaces
except ImportError:
    netifaces = None

from archey.entry import Entry


class LanIp(Entry):
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

        address_types = [netifaces.AF_INET]
        if self._configuration.get('ip_settings')['lan_ip_v6_support']:
            address_types.append(netifaces.AF_INET6)

        self.value = []

        # Loop through all available network interfaces.
        for if_name in netifaces.interfaces():
            # Fetch associated addresses elements.
            if_addrs = netifaces.ifaddresses(if_name)

            # For each IPv4 (or IPv6 address)...
            for addr_type in address_types:
                if addr_type not in if_addrs:
                    continue

                for if_addr in if_addrs[addr_type]:
                    # Filter out loopback addresses.
                    if (addr_type == netifaces.AF_INET and if_addr['addr'].startswith('127.')) \
                        or if_addr['addr'] == '::1':
                        continue

                    self.value.append(if_addr['addr'].split('%')[0])

        lan_ip_max_count = self._configuration.get('ip_settings')['lan_ip_max_count']
        if lan_ip_max_count is not False:
            self.value = self.value[:lan_ip_max_count]


    def output(self, output):
        """Adds the entry to `output` after pretty-formatting the IP address list."""
        # If we found IP addresses, join them together nicely.
        # If not, fall back on default strings according to `netifaces` availability.
        if self.value:
            text_output = ', '.join(self.value)
        elif netifaces:
            text_output = self._configuration.get('default_strings')['no_address']
        else:
            text_output = self._configuration.get('default_strings')['not_detected']

        output.append(self.name, text_output)
