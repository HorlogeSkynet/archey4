"""Public IP address detection class"""

from socket import timeout as SocketTimeoutError
from subprocess import DEVNULL, CalledProcessError, TimeoutExpired, check_output
from typing import Optional, TypeVar
from urllib.error import URLError
from urllib.request import urlopen

from archey.entry import Entry
from archey.environment import Environment

Self = TypeVar("Self", bound="WanIP")


class WanIP(Entry):
    """Uses different ways to retrieve the public IPv{4,6} addresses"""

    _ICON = "\U000f0a60"  # md_ip_network
    _PRETTY_NAME = "WAN IP"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = []

        if Environment.DO_NOT_TRACK:
            return

        ipv4_addr = self._retrieve_ip_address(4)
        if ipv4_addr:
            self.value.append(ipv4_addr)

        ipv6_addr = self._retrieve_ip_address(6)
        if ipv6_addr:
            self.value.append(ipv6_addr)

    def _retrieve_ip_address(self, ip_version: int) -> Optional[str]:
        """
        Best effort to retrieve public IP address based on corresponding options.
        We are trying special DNS resolutions first for performance and (system) caching purposes.
        """
        options = self.options.get(f"ipv{ip_version}", {})

        # Is retrieval enabled for this IP version ?
        if not options and not isinstance(options, dict):
            return None

        # Is retrieval via DNS query enabled ?
        dns_query = options.get("dns_query", "myip.opendns.com")
        if dns_query:
            # Run the DNS query.
            ip_address = self._run_dns_query(
                dns_query,
                options.get("dns_resolver", "resolver1.opendns.com"),
                ip_version,
                options.get("dns_timeout", 1),
            )
            # Return IP only if the query was successful
            if ip_address is not None:
                return ip_address

        # Is retrieval via HTTP(S) request enabled ?
        http_url = options.get("http_url", f"https://v{ip_version}.ident.me/")
        if not http_url:
            return None

        # Run the HTTP(S) request.
        return self._run_http_request(http_url, options.get("http_timeout", 1))

    @staticmethod
    def _run_dns_query(query: str, resolver: str, ip_version: int, timeout: float) -> Optional[str]:
        """Simple wrapper to `dig` command to perform DNS queries"""
        try:
            ip_address = check_output(
                [
                    "dig",
                    "+short",
                    ("-" + str(ip_version)),
                    ("AAAA" if ip_version == 6 else "A"),
                    query,
                    "@" + resolver,
                ],
                timeout=timeout,
                stderr=DEVNULL,
                universal_newlines=True,
            ).rstrip()
        except (FileNotFoundError, TimeoutExpired, CalledProcessError):
            return None

        # `ip_address` might be empty here.
        return ip_address

    @staticmethod
    def _run_http_request(server_url: str, timeout: float) -> Optional[str]:
        """Simple wrapper to `urllib` module to perform HTTP requests"""
        try:
            with urlopen(server_url, timeout=timeout) as http_request:
                return http_request.read().decode().strip()
        except (URLError, SocketTimeoutError):
            return None

    def __iter__(self: Self) -> Self:
        """Sets up iterable over IP addresses"""
        if not self.value and not Environment.DO_NOT_TRACK:
            # If no IP addresses found, fall-back on the "No address" string.
            self._iter_value = iter([self._default_strings.get("no_address")])
        else:
            self._iter_value = iter(self.value)
        return self

    def __next__(self) -> Entry.ValueType:
        """Yield IP addresses."""
        return (self.name, str(next(self._iter_value)))
