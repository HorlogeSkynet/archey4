"""Public IP address detection class"""

import sys

from subprocess import check_output, DEVNULL, TimeoutExpired, CalledProcessError

from archey.configuration import Configuration


class WanIp:
    """Uses different ways to retrieve the public IPv{4,6} addresses"""
    def __init__(self):
        # The configuration object is needed to retrieve some settings below.
        configuration = Configuration()

        # IPv6 address retrieval (unless the user doesn't want it).
        if configuration.get('ip_settings')['wan_ip_v6_support']:
            try:
                ipv6_value = check_output(
                    [
                        'dig', '+short', '-6', 'AAAA', 'myip.opendns.com',
                        '@resolver1.ipv6-sandbox.opendns.com'
                    ],
                    timeout=configuration.get('timeout')['ipv6_detection'],
                    stderr=DEVNULL, universal_newlines=True
                ).rstrip()

            except (FileNotFoundError, TimeoutExpired, CalledProcessError):
                try:
                    ipv6_value = check_output(
                        [
                            'wget', '-q6O-', 'https://v6.ident.me/'
                        ],
                        timeout=configuration.get('timeout')['ipv6_detection'],
                        universal_newlines=True
                    )

                except (CalledProcessError, TimeoutExpired):
                    # It looks like this user doesn't have any IPv6 address...
                    # ... or is not connected to Internet.
                    ipv6_value = None

                except FileNotFoundError:
                    ipv6_value = None
                    print('Warning: `wget` has not been found on your system.',
                          file=sys.stderr)

        else:
            ipv6_value = None

        # IPv4 addresses retrieval (anyway).
        try:
            ipv4_value = check_output(
                [
                    'dig', '+short', '-4', 'A', 'myip.opendns.com',
                    '@resolver1.opendns.com'
                ],
                timeout=configuration.get('timeout')['ipv4_detection'],
                stderr=DEVNULL, universal_newlines=True
            ).rstrip()

        except (FileNotFoundError, TimeoutExpired, CalledProcessError):
            try:
                ipv4_value = check_output(
                    [
                        'wget', '-q4O-', 'https://v4.ident.me/'
                    ],
                    timeout=configuration.get('timeout')['ipv4_detection'],
                    universal_newlines=True
                )

            except (CalledProcessError, TimeoutExpired):
                # This user looks not connected to Internet...
                ipv4_value = None

            except FileNotFoundError:
                ipv4_value = None
                # If statement so as to not print the same message twice.
                if not configuration.get('ip_settings')['wan_ip_v6_support']:
                    print('Warning: `wget` has not been found on your system.',
                          file=sys.stderr)

        self.value = ', '.join(
            filter(None, (ipv4_value, ipv6_value))
        ) or configuration.get('default_strings')['no_address']
