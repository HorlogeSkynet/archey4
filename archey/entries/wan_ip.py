"""Public IP address detection class"""

from socket import timeout as SocketTimeoutError
from subprocess import check_output, DEVNULL, TimeoutExpired, CalledProcessError
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from archey.entry import Entry


class WanIp(Entry):
    """Uses different ways to retrieve the public IPv{4,6} addresses"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = []

        self._retrieve_ipv4_address()

        # IPv6 address retrieval (unless the user doesn't want it).
        if self._configuration.get('ip_settings')['wan_ip_v6_support']:
            self._retrieve_ipv6_address()

        self.value = list(filter(None, self.value))

    def _retrieve_ipv4_address(self):
        try:
            ipv4_addr = check_output(
                [
                    'dig', '+short', '-4', 'A', 'myip.opendns.com',
                    '@resolver1.opendns.com'
                ],
                timeout=self._configuration.get('timeout')['ipv4_detection'],
                stderr=DEVNULL, universal_newlines=True
            ).rstrip()
        except (FileNotFoundError, TimeoutExpired, CalledProcessError):
            try:
                ipv4_addr = urlopen(
                    'https://v4.ident.me/',
                    timeout=self._configuration.get('timeout')['ipv4_detection']
                )
            except (HTTPError, URLError, SocketTimeoutError):
                # The machine does not seem to be connected to Internet...
                return

            ipv4_addr = ipv4_addr.read().decode().strip()

        self.value.append(ipv4_addr)

    def _retrieve_ipv6_address(self):
        try:
            ipv6_addr = check_output(
                [
                    'dig', '+short', '-6', 'AAAA', 'myip.opendns.com',
                    '@resolver1.ipv6-sandbox.opendns.com'
                ],
                timeout=self._configuration.get('timeout')['ipv6_detection'],
                stderr=DEVNULL, universal_newlines=True
            ).rstrip()
        except (FileNotFoundError, TimeoutExpired, CalledProcessError):
            try:
                response = urlopen(
                    'https://v6.ident.me/',
                    timeout=self._configuration.get('timeout')['ipv6_detection']
                )
            except (HTTPError, URLError, SocketTimeoutError):
                # It looks like this machine doesn't have any IPv6 address...
                # ... or is not connected to Internet.
                return

            ipv6_addr = response.read().decode().strip()

        self.value.append(ipv6_addr)


    def output(self, output):
        """Adds the entry to `output` after pretty-formatting our list of IP addresses."""
        # If we found IP addresses, join them together nicely.
        # If not, fall-back on the "No address" string.
        output.append(
            self.name,
            ', '.join(self.value) or self._configuration.get('default_strings')['no_address']
        )
