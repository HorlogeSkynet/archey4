#!/usr/bin/env python3


import os
import re
import sys

from enum import Enum
from glob import glob
from subprocess import CalledProcessError, DEVNULL, PIPE, Popen, \
    TimeoutExpired, check_output

import distro

from output import Output
from hostname import Hostname
from configuration import Configuration
from constants import (
    COLOR_DICT,
    DE_DICT,
    WM_DICT,
)

# ---------- Global variables --------- #

# We create a global instance of our `Configuration` Class
CONFIG = Configuration()

# We'll list the running processes only one time
try:
    PROCESSES = check_output(
        ['ps', '-u' + str(os.getuid()) if os.getuid() != 0 else '-ax',
         '-o', 'comm', '--no-headers'], universal_newlines=True
    ).splitlines()

except FileNotFoundError:
    print('Please, install first `procps` on your distribution.',
          file=sys.stderr)
    exit()

# -------------- Entries -------------- #

class User:
    def __init__(self):
        self.value = os.getenv(
            'USER',
            CONFIG.get('default_strings')['not_detected']
        )




class Model:
    def __init__(self):
        try:
            with open('/sys/devices/virtual/dmi/id/product_name') as file:
                model = file.read().rstrip()

        except FileNotFoundError:
            # The file above does not exist, is this device a Raspberry Pi ?
            # Let's retrieve the Hardware and Revision IDs with `/proc/cpuinfo`
            with open('/proc/cpuinfo') as file:
                output = file.read()

            hardware = re.search('(?<=Hardware\t: ).*', output)
            revision = re.search('(?<=Revision\t: ).*', output)

            # If the output contains 'Hardware' and 'Revision'...
            if hardware and revision:
                # ... let's set a pretty info string with these data
                model = 'Raspberry Pi {0} (Rev. {1})'.format(
                    hardware.group(0),
                    revision.group(0)
                )

            else:
                # A tricky way to retrieve some details about hypervisor...
                # ... within virtual contexts.
                # `archey` needs to be run as root although.
                try:
                    virt_what = ', '.join(
                        check_output(
                            ['virt-what'],
                            stderr=DEVNULL, universal_newlines=True
                        ).splitlines()
                    )

                    if virt_what:
                        try:
                            # Sometimes we may gather info added by...
                            # ... hosting service provider this way
                            model = check_output(
                                ['dmidecode', '-s', 'system-product-name'],
                                stderr=DEVNULL, universal_newlines=True
                            ).rstrip()

                        except (FileNotFoundError, CalledProcessError):
                            model = CONFIG.get(
                                'default_strings'
                            )['virtual_environment']

                        model += ' ({0})'.format(virt_what)

                    else:
                        model = CONFIG.get(
                            'default_strings'
                        )['bare_metal_environment']

                except (FileNotFoundError, CalledProcessError):
                    model = CONFIG.get('default_strings')['not_detected']

        self.value = model


class Distro:
    def __init__(self):
        self.value = '{0} [{1}]'.format(
            distro.name(pretty=True),
            check_output(
                ['uname', '-m'],
                universal_newlines=True
            ).rstrip()
        )


class Kernel:
    def __init__(self):
        self.value = check_output(
            ['uname', '-r'],
            universal_newlines=True
        ).rstrip()


class Uptime:
    def __init__(self):
        with open('/proc/uptime') as file:
            fuptime = int(file.read().split('.')[0])

        day, fuptime = divmod(fuptime, 86400)
        hour, fuptime = divmod(fuptime, 3600)
        minute = fuptime // 60

        uptime = ''
        if day:
            uptime += str(day) + ' day'
            if day > 1:
                uptime += 's'

            if hour or minute:
                if bool(hour) != bool(minute):
                    uptime += ' and '

                else:
                    uptime += ', '

        if hour:
            uptime += str(hour) + ' hour'
            if hour > 1:
                uptime += 's'

            if minute:
                uptime += ' and '

        if minute:
            uptime += str(minute) + ' minute'
            if minute > 1:
                uptime += 's'

        else:
            if not day and not hour:
                uptime = '< 1 minute'

        self.value = uptime


class WindowManager:
    def __init__(self):
        try:
            window_manager = re.search(
                '(?<=Name: ).*',
                check_output(
                    ['wmctrl', '-m'],
                    stderr=DEVNULL, universal_newlines=True
                )
            ).group(0)

        except (FileNotFoundError, CalledProcessError):
            for key, value in WM_DICT.items():
                if key in PROCESSES:
                    window_manager = value
                    break

            else:
                window_manager = CONFIG.get('default_strings')['not_detected']

        self.value = window_manager


class DesktopEnvironment:
    def __init__(self):
        for key, value in DE_DICT.items():
            if key in PROCESSES:
                desktop_environment = value
                break

        else:
            # Let's rely on an environment var if the loop above didn't `break`
            desktop_environment = os.getenv(
                'XDG_CURRENT_DESKTOP',
                CONFIG.get('default_strings')['not_detected']
            )

        self.value = desktop_environment


class Shell:
    def __init__(self):
        self.value = os.getenv(
            'SHELL',
            CONFIG.get('default_strings')['not_detected']
        )


class Terminal:
    def __init__(self):
        terminal = os.getenv(
            'TERM',
            CONFIG.get('default_strings')['not_detected']
        )

        # On systems with non-Unicode locales, we imitate '\u2588' character
        # ... with '#' to display the terminal colors palette.
        # This is the default option for backward compatibility.
        colors = ' '.join([
            '\x1b[0;3{0}m{1}\x1b[1;3{0}m{1}{2}'.format(
                i,
                '\u2588' if CONFIG.get('colors_palette')['use_unicode']
                else '#',
                COLOR_DICT['clear']
            ) for i in range(7, 0, -1)
        ])

        self.value = '{0} {1}'.format(terminal, colors)


class Temperature:
    def __init__(self):
        temps = []

        try:
            # Let's try to retrieve a value from the Broadcom chip on Raspberry
            temp = float(
                re.search(
                    r'\d+\.\d+',
                    check_output(
                        ['/opt/vc/bin/vcgencmd', 'measure_temp'],
                        stderr=DEVNULL, universal_newlines=True
                    )
                ).group(0)
            )

            temps.append(
                self._convert_to_fahrenheit(temp)
                if CONFIG.get('temperature')['use_fahrenheit'] else temp
            )

        except (FileNotFoundError, CalledProcessError):
            pass

        # Now we just check for values within files present in the path below
        for thermal_file in glob('/sys/class/thermal/thermal_zone*/temp'):
            with open(thermal_file) as file:
                try:
                    temp = float(file.read().strip()) / 1000

                except OSError:
                    continue

                if temp != 0.0:
                    temps.append(
                        self._convert_to_fahrenheit(temp)
                        if CONFIG.get('temperature')['use_fahrenheit'] else temp
                    )

        if temps:
            self.value = '{0}{1}{2}'.format(
                str(round(sum(temps) / len(temps), 1)),
                CONFIG.get('temperature')['char_before_unit'],
                'F' if CONFIG.get('temperature')['use_fahrenheit'] else 'C'
            )

            if len(temps) > 1:
                self.value += ' (Max. {0}{1}{2})'.format(
                    str(round(max(temps), 1)),
                    CONFIG.get('temperature')['char_before_unit'],
                    'F' if CONFIG.get('temperature')['use_fahrenheit'] else 'C'
                )

        else:
            self.value = CONFIG.get('default_strings')['not_detected']

    @staticmethod
    def _convert_to_fahrenheit(temp):
        """
        Simple Celsius to Fahrenheit conversion method
        """
        return temp * (9 / 5) + 32


class Packages:
    def __init__(self):
        for packages_tool in [['dnf', 'list', 'installed'],
                              ['dpkg', '--get-selections'],
                              ['emerge', '-ep', 'world'],
                              ['pacman', '-Q'],
                              ['rpm', '-qa'],
                              ['yum', 'list', 'installed'],
                              ['zypper', 'search', '-i']]:
            try:
                results = check_output(
                    packages_tool,
                    stderr=DEVNULL, env={'LANG': 'C'}, universal_newlines=True
                )
                packages = results.count('\n')

                if 'dnf' in packages_tool:  # Deduct extra heading line
                    packages -= 1

                elif 'dpkg' in packages_tool:  # Packages removed but not purged
                    packages -= results.count('deinstall')

                elif 'emerge' in packages_tool:  # Deduct extra heading lines
                    packages -= 5

                elif 'yum' in packages_tool:  # Deduct extra heading lines
                    packages -= 2

                elif 'zypper' in packages_tool:  # Deduct extra heading lines
                    packages -= 5

                break

            except (FileNotFoundError, CalledProcessError):
                pass

        else:
            packages = CONFIG.get('default_strings')['not_detected']

        self.value = packages


class CPU:
    def __init__(self):
        model_name_regex = re.compile(
            r'^model name\s*:\s*(.*)$',
            flags=re.IGNORECASE | re.MULTILINE
        )

        with open('/proc/cpuinfo') as file:
            cpuinfo = re.search(model_name_regex, file.read())

        # This test case has been built for some ARM architectures (see #29).
        # Sometimes, `model name` info is not present within `/proc/cpuinfo`.
        # We use the output of `lscpu` program (util-linux-ng) to retrieve it.
        if not cpuinfo:
            cpuinfo = re.search(
                model_name_regex,
                check_output(
                    ['lscpu'],
                    env={'LANG': 'C'}, universal_newlines=True
                )
            )

        # Sometimes CPU model name contains extra ugly white-spaces.
        self.value = re.sub(r'\s+', ' ', cpuinfo.group(1))


class GPU:
    def __init__(self):
        """
        Some explanations are needed here :
        * We call `lspci` program to retrieve hardware devices
        * We keep only the entries with "3D", "VGA" or "Display"
        * We sort them in the same order as above (for relevancy)
        """
        try:
            lspci_output = sorted(
                [
                    i.split(': ')[1] for i in check_output(
                        ['lspci'], universal_newlines=True
                    ).splitlines()
                    if '3D' in i or 'VGA' in i or 'Display' in i
                ], key=len
            )

            if lspci_output:
                gpuinfo = lspci_output[0]

                # If the line got too long, let's truncate it and add some dots
                if len(gpuinfo) > 48:
                    # This call truncates `gpuinfo` with words preservation
                    gpuinfo = re.search(
                        r'.{1,45}(?:\s|$)', gpuinfo
                    ).group(0).strip() + '...'

            else:
                gpuinfo = CONFIG.get('default_strings')['not_detected']

        except (FileNotFoundError, CalledProcessError):
            gpuinfo = CONFIG.get('default_strings')['not_detected']

        self.value = gpuinfo


class RAM:
    def __init__(self):
        try:
            ram = ''.join(
                filter(
                    re.compile('Mem').search,
                    check_output(
                        ['free', '-m'],
                        env={'LANG': 'C'}, universal_newlines=True
                    ).splitlines()
                )
            ).split()
            used = float(ram[2])
            total = float(ram[1])

        except (IndexError, FileNotFoundError):
            # An in-digest one-liner to retrieve memory info into a dictionary
            with open('/proc/meminfo') as file:
                ram = {
                    i.split(':')[0]: float(i.split(':')[1].strip(' kB')) / 1024
                    for i in filter(None, file.read().splitlines())
                }

            total = ram['MemTotal']
            # Here, let's imitate the `free` command behavior
            # (https://gitlab.com/procps-ng/procps/blob/master/proc/sysinfo.c#L787)
            used = total - (ram['MemFree'] + ram['Cached'] + ram['Buffers'])
            if used < 0:
                used += ram['Cached'] + ram['Buffers']

        self.value = '{0}{1} MB{2} / {3} MB'.format(
            COLOR_DICT['sensors'][int(((used / total) * 100) // 33.34)],
            int(used),
            COLOR_DICT['clear'],
            int(total)
        )


class Disk:
    def __init__(self):
        total = re.sub(
            ',', '.',
            check_output(
                [
                    'df', '-Tlh', '-B', 'GB', '--total',
                    '-t', 'ext4', '-t', 'ext3', '-t', 'ext2',
                    '-t', 'reiserfs', '-t', 'jfs', '-t', 'zfs',
                    '-t', 'ntfs', '-t', 'fat32', '-t', 'btrfs',
                    '-t', 'fuseblk', '-t', 'xfs', '-t', 'simfs',
                    '-t', 'tmpfs', '-t', 'lxfs'
                ], universal_newlines=True
            ).splitlines()[-1]
        ).split()

        self.value = '{0}{1}{2} / {3}'.format(
            COLOR_DICT['sensors'][int(float(total[5][:-1]) // 33.34)],
            re.sub('GB', ' GB', total[3]),
            COLOR_DICT['clear'],
            re.sub('GB', ' GB', total[2])
        )


class LanIp:
    def __init__(self):
        try:
            addresses = check_output(
                ['hostname', '-I'],
                stderr=DEVNULL, universal_newlines=True
            ).split()

        except (CalledProcessError, FileNotFoundError):
            # Slow manual workaround for old `inetutils` versions, with `ip`
            addresses = check_output(
                ['cut', '-d', ' ', '-f', '4'],
                universal_newlines=True,
                stdin=Popen(
                    ['cut', '-d', '/', '-f', '1'],
                    stdout=PIPE,
                    stdin=Popen(
                        ['tr', '-s', ' '],
                        stdout=PIPE,
                        stdin=Popen(
                            ['grep', '-E', 'scope (global|site)'],
                            stdout=PIPE,
                            stdin=Popen(
                                ['ip', '-o', 'addr', 'show', 'up'],
                                stdout=PIPE
                            ).stdout
                        ).stdout
                    ).stdout
                ).stdout
            ).splitlines()

        # Use list slice to save only `lan_ip_max_count` from `addresses`.
        # If set to `False`, don't modify the list.
        # This option is still optional.
        self.value = ', '.join(
            addresses[:(
                CONFIG.get('ip_settings')['lan_ip_max_count']
                if CONFIG.get('ip_settings')['lan_ip_max_count'] is not False
                else len(addresses)
            )]
        ) or CONFIG.get('default_strings')['no_address']


class WanIp:
    def __init__(self):
        # IPv6 address retrieval (unless the user doesn't want it).
        if CONFIG.get('ip_settings')['wan_ip_v6_support']:
            try:
                ipv6_value = check_output(
                    [
                        'dig', '+short', '-6', 'AAAA', 'myip.opendns.com',
                        '@resolver1.ipv6-sandbox.opendns.com'
                    ],
                    timeout=CONFIG.get('timeout')['ipv6_detection'],
                    stderr=DEVNULL, universal_newlines=True
                ).rstrip()

            except (FileNotFoundError, TimeoutExpired, CalledProcessError):
                try:
                    ipv6_value = check_output(
                        [
                            'wget', '-q6O-', 'https://v6.ident.me/'
                        ],
                        timeout=CONFIG.get('timeout')['ipv6_detection'],
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
                timeout=CONFIG.get('timeout')['ipv4_detection'],
                stderr=DEVNULL, universal_newlines=True
            ).rstrip()

        except (FileNotFoundError, TimeoutExpired, CalledProcessError):
            try:
                ipv4_value = check_output(
                    [
                        'wget', '-q4O-', 'https://v4.ident.me/'
                    ],
                    timeout=CONFIG.get('timeout')['ipv4_detection'],
                    universal_newlines=True
                )

            except (CalledProcessError, TimeoutExpired):
                # This user looks not connected to Internet...
                ipv4_value = None

            except FileNotFoundError:
                ipv4_value = None
                # If statement so as to not print the same message twice.
                if not CONFIG.get('ip_settings')['wan_ip_v6_support']:
                    print('Warning: `wget` has not been found on your system.',
                          file=sys.stderr)

        self.value = ', '.join(
            filter(None, (ipv4_value, ipv6_value))
        ) or CONFIG.get('default_strings')['no_address']


# ----------- Classes Index ----------- #

class Classes(Enum):
    User = User
    Hostname = Hostname
    Model = Model
    Distro = Distro
    Kernel = Kernel
    Uptime = Uptime
    WindowManager = WindowManager
    DesktopEnvironment = DesktopEnvironment
    Shell = Shell
    Terminal = Terminal
    Packages = Packages
    Temperature = Temperature
    CPU = CPU
    GPU = GPU
    RAM = RAM
    Disk = Disk
    LAN_IP = LanIp
    WAN_IP = WanIp


# ---------------- Main --------------- #

def main():
    output = Output()
    for key in Classes:
        if CONFIG.get('entries', {}).get(key.name, True):
            output.append(key.name, key.value().value)

    output.output()


if __name__ == '__main__':
    main()
