"""Local IP addresses detection class"""

import ipaddress
from itertools import islice
from typing import Iterator, TypeVar

try:
    import netifaces
except ImportError:
    netifaces = None

from archey.entry import Entry

Self = TypeVar("Self", bound="LanIP")


class LanIP(Entry):
    """Relies on the `netifaces` module to detect LAN IP addresses"""

    _ICON = "\U000f0a60"  # md_ip_network
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

        # Link-local IP addresses (in RFC3927 terms) will be shown by default.
        show_link_local = bool(self.options.get("show_link_local", True))

        self.value = list(
            islice(
                self._lan_ip_addresses_generator(addr_families, show_global, show_link_local),
                max_count,
            )
        )

    @staticmethod
    def _lan_ip_addresses_generator(
        addr_families: list, show_global: bool, show_link_local: bool
    ) -> Iterator[str]:
        """Generator yielding local IP address according to passed address families"""
        # Loop through all available network interfaces.
        for if_name in netifaces.interfaces():
            # Fetch associated addresses elements.
            if_addrs = netifaces.ifaddresses(if_name)

            for addr_family in addr_families:
                for if_addr in if_addrs.get(addr_family, []):
                    # IPv6 addresses may contain '%' token separator.
                    ip_addr = ipaddress.ip_address(if_addr["addr"].split("%")[0])

                    # Filter out loopback and public/link-local IP addresses (if enabled).
                    if (
                        not ip_addr.is_loopback
                        and (not ip_addr.is_global or show_global)
                        and (not ip_addr.is_link_local or show_link_local)
                    ):
                        # Finally, yield the address compressed representation.
                        yield ip_addr.compressed

    def __iter__(self: Self) -> Self:
        """Sets up iterable over IP addresses"""
        if not self.value and netifaces:
            # If no IP addresses found, fall-back on the "No address" string.
            self._iter_value = iter([self._default_strings.get("no_address")])
        elif not self.value:
            self._iter_value = iter([])
        else:
            self._iter_value = iter(self.value)
        return self

    def __next__(self) -> Entry.ValueType:
        """Yield IP addresses."""
        return (self.name, str(next(self._iter_value)))
