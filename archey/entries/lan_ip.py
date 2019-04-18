"""Local IP addresses detection class"""

import netifaces


class LanIp:
    """Relies on the `netifaces` module to detect LAN IP addresses"""
    def __init__(self, ip_max_count=False, no_address=None):
        addresses = []

        # Loop through all available network interfaces.
        for interface in netifaces.interfaces():
            # Fetch associated addresses elements.
            interface_addrs = netifaces.ifaddresses(interface)

            # For each IPv4 or IPv6 address...
            for addr_type in [netifaces.AF_INET, netifaces.AF_INET6]:
                if addr_type in interface_addrs:
                    for interface_addr in interface_addrs[addr_type]:
                        # Filter out loopback addresses.
                        if (addr_type != netifaces.AF_INET or \
                                not interface_addr['addr'].startswith('127.')) and \
                                interface_addr['addr'] != '::1':
                            addresses.append(interface_addr['addr'].split('%')[0])

        if ip_max_count is not False:
            addresses = addresses[:ip_max_count]

        self.value = ', '.join(addresses) or no_address
