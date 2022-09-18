"""Public IP address detection class"""

from socket import timeout as SocketTimeoutError
from subprocess import DEVNULL, CalledProcessError, TimeoutExpired, check_output
from typing import Optional
from urllib.error import URLError
from urllib.request import urlopen

from archey.entry import Entry
from archey.environment import Environment


class WanIP(Entry):
    """Uses different ways to retrieve the public IPv{4,6} addresses"""

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
            try:
                ip_address = self._run_dns_query(
                    dns_query,
                    options.get("dns_resolver", "resolver1.opendns.com"),
                    ip_version,
                    options.get("dns_timeout", 1),
                )
            except FileNotFoundError:
                # DNS lookup tool does not seem to be available.
                pass
            else:
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
        except (TimeoutExpired, CalledProcessError):
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

    def output(self, output) -> None:
        """Adds the entry to `output` after pretty-formatting our list of IP addresses."""
        # If we found IP addresses, join them together nicely.
        # If not, fall-back on the "No address" string.
        if self.value:
            if not self.options.get("one_line", True):
                # One-line output has been disabled, add one IP address per item.
                for ip_address in self.value:
                    output.append(self.name, ip_address)

                return

            text_output = ", ".join(self.value)

        elif not Environment.DO_NOT_TRACK:
            text_output = self._default_strings.get("no_address")
        else:
            text_output = self._default_strings.get("not_detected")

        output.append(self.name, text_output)
