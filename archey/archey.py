#!/usr/bin/env python3


import os
import re
import sys

from enum import Enum
from subprocess import CalledProcessError, DEVNULL, check_output

import distro

from output import Output
from configuration import Configuration
import entries
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


class Distro:
    def __init__(self):
        self.value = '{0} [{1}]'.format(
            distro.name(pretty=True),
            check_output(
                ['uname', '-m'],
                universal_newlines=True
            ).rstrip()
        )


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


# ----------- Classes Index ----------- #

class Classes(Enum):
    User = {
        'class': entries.User,
        'kwargs': {
            'not_detected': CONFIG.get('default_strings')['not_detected']
        }
    }
    Hostname = {'class': entries.Hostname}
    Model = {'class': entries.Model}
    Distro = {'class': Distro}
    Kernel = {'class': entries.Kernel}
    Uptime = {'class': entries.Uptime}
    WindowManager = {'class': WindowManager}
    DesktopEnvironment = {'class': DesktopEnvironment}
    Shell = {'class': Shell}
    Terminal = {
        'class': entries.Terminal,
        'not_detected': CONFIG.get('default_strings')['not_detected'],
        'use_unicode': CONFIG.get('colors_palette')['use_unicode'],
        'clear_color': COLOR_DICT['clear']
    }
    Packages = {
        'class': entries.Packages,
        'kwargs': {
            'not_detected': CONFIG.get('default_strings')['not_detected']
        }
    }
    Temperature = {
        'class': entries.Temperature,
        'kwargs': {
            'use_fahrenheit': CONFIG.get('temperature')['use_fahrenheit'],
            'char_before_unit': CONFIG.get('temperature')['char_before_unit'],
            'not_detected': CONFIG.get('default_strings')['not_detected']
        }
    }
    CPU = {'class': entries.CPU}
    GPU = {
         'class': entries.GPU,
         'kwargs': {
           'not_detected': CONFIG.get('default_strings')['not_detected']
         }
    }
    RAM = {'class': entries.RAM}
    Disk = {'class': entries.Disk}
    LAN_IP = {
        'class': entries.LanIp,
        'kwargs': {
            'ip_max_count': CONFIG.get('ip_settings')['lan_ip_max_count'],
            'no_address': CONFIG.get('default_strings')['no_address']
        }
    }
    WAN_IP = {
        'class': entries.WanIp,
        'kwargs': {
            'ipv6_support': CONFIG.get('ip_settings')['wan_ip_v6_support'],
            'ipv6_timeout': CONFIG.get('timeout')['ipv6_detection'],
            'ipv4_timeout': CONFIG.get('timeout')['ipv4_detection'],
            'no_address': CONFIG.get('default_strings')['no_address']
        }
    }


# ---------------- Main --------------- #

def main():
    output = Output()
    for key in Classes:
        if CONFIG.get('entries', {}).get(key.name, True):
            kwargs = key.value.get('kwargs', {})
            value = key.value['class'](**kwargs).value
            output.append(key.name, value)

    output.output()


if __name__ == '__main__':
    main()
