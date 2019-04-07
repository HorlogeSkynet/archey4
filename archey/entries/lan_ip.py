import netifaces


class LanIp:
    def __init__(self, ip_max_count=False, no_address=None):
        addresses = None
        interfaces = netifaces.interfaces()
        if interfaces:
            addresses = [
                netifaces.ifaddresses(interface)[2][0]['addr']
                for interface in netifaces.interfaces()
            ]
            max_count = ip_max_count
            if max_count is not False:
                addresses = ', '.join(addresses[:max_count])
        self.value = addresses or no_address
