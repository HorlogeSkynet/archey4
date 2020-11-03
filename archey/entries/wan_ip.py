"""Public IP address detection class"""

from socket import timeout as SocketTimeoutError
from subprocess import check_output, DEVNULL, TimeoutExpired, CalledProcessError
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from archey.entry import Entry


class WanIP(Entry):
    """Uses different ways to retrieve the public IPv{4,6} addresses"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = []

        ipv4_addr = self._retrieve_ip_address(4)
        if ipv4_addr:
            self.value.append(ipv4_addr)

        ipv6_addr = self._retrieve_ip_address(6)
        if ipv6_addr:
            self.value.append(ipv6_addr)


    def _retrieve_ip_address(self, ip_version):
        """
        Best effort to retrieve public IP address based on corresponding options.
        We are trying special DNS resolutions first for performance and (system) caching purposes.
        """
        options = self.options.get('ipv{}'.format(ip_version), {})

        # Is retrieval enabled for this IP version ?
        if not options and options != {}:
            return None

        # Is retrieval via DNS query enabled ?
        dns_query = options.get('dns_query', 'myip.opendns.com')
        if dns_query:
            # Run the DNS query.
            try:
                ip_address = self._run_dns_query(
                    dns_query,
                    options.get('dns_resolver', 'resolver1.opendns.com'),
                    ip_version,
                    options.get('dns_timeout', 1)
                )
            except FileNotFoundError:
                # DNS lookup tool does not seem to be available.
                pass
            else:
                return ip_address

        # Is retrieval via HTTP(S) request enabled ?
        http_url = options.get('http_url', 'https://v{}.ident.me/'.format(ip_version))
        if not http_url:
            return None

        # Run the HTTP(S) request.
        return self._run_http_request(
            http_url,
            options.get('http_timeout', 1)
        )


    @staticmethod
    def _run_dns_query(query, resolver, ip_version, timeout):
        """Simple wrapper to `dig` command to perform DNS queries"""
        try:
            ip_address = check_output(
                [
                    'dig', '+short',
                    ('-' + str(ip_version)),
                    ('AAAA' if ip_version == 6 else 'A'),
                    query, '@' + resolver
                ],
                timeout=timeout,
                stderr=DEVNULL, universal_newlines=True
            ).rstrip()
        except (TimeoutExpired, CalledProcessError):
            return None

        # `ip_address` might be empty here.
        return ip_address

    @staticmethod
    def _run_http_request(server_url, timeout):
        """Simple wrapper to `urllib` module to perform HTTP requests"""
        try:
            http_request = urlopen(
                server_url,
                timeout=timeout
            )
        except (HTTPError, URLError, SocketTimeoutError):
            return None

        return http_request.read().decode().strip()


    def output(self, output):
        """Adds the entry to `output` after pretty-formatting our list of IP addresses."""
        # If we found IP addresses, join them together nicely.
        # If not, fall-back on the "No address" string.
        output.append(
            self.name,
            ', '.join(self.value) or self._default_strings.get('no_address')
        )
