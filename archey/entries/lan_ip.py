"""Local IP addresses detection class"""

import ipaddress
from itertools import islice
from typing import Iterator

try:
    import netifaces
except ImportError:
    netifaces = None

from archey.entry import Entry


class LanIP(Entry):
    """Relies on the `netifaces` module to detect LAN IP addresses"""

    _PRETTY_NAME = "LAN IP"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not netifaces:
            self._logger.warning(
                "`netifaces` Python module couldn't be found. "
                "Please either install it or explicitly disable `LAN_IP` entry in configuration."
            )
            return

        # IPv4 will be enabled by default.
        addr_families = [netifaces.AF_INET]
        if self.options.get("ipv6_support", True):
            addr_families.append(netifaces.AF_INET6)

        max_count = self.options.get("max_count", 2)
        # Consistency with other entries' configuration: Infinite count if false.
        if max_count is False:
            max_count = None

        # Global IP addresses (in RFC1918 terms) will be hidden by default.
        show_global = bool(self.options.get("show_global"))

        self.value = list(
            islice(self._lan_ip_addresses_generator(addr_families, show_global), max_count)
        )

    @staticmethod
    def _lan_ip_addresses_generator(addr_families: list, show_global: bool) -> Iterator[str]:
        """Generator yielding local IP address according to passed address families"""
        # Loop through all available network interfaces.
        for if_name in netifaces.interfaces():
            # Fetch associated addresses elements.
            if_addrs = netifaces.ifaddresses(if_name)

            for addr_family in addr_families:
                for if_addr in if_addrs.get(addr_family, []):
                    # IPv6 addresses may contain '%' token separator.
                    ip_addr = ipaddress.ip_address(if_addr["addr"].split("%")[0])

                    # Filter out loopback and public IP addresses.
                    if not ip_addr.is_loopback and (not ip_addr.is_global or show_global):
                        # Finally, yield the address compressed representation.
                        yield ip_addr.compressed

    def output(self, output) -> None:
        """Adds the entry to `output` after pretty-formatting the IP address list."""
        # If we found IP addresses, join them together nicely.
        # If not, fall back on default strings according to `netifaces` availability.
        if self.value:
            if not self.options.get("one_line", True):
                # One-line output has been disabled, add one IP address per item.
                for ip_address in self.value:
                    output.append(self.name, ip_address)

                return

            text_output = ", ".join(self.value)

        elif netifaces:
            text_output = self._default_strings.get("no_address")
        else:
            text_output = self._default_strings.get("not_detected")

        output.append(self.name, text_output)
