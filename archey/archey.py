#!/usr/bin/env python3


import os
import re
import sys

from enum import Enum
from subprocess import CalledProcessError, DEVNULL, check_output

import distro

from output import Output
from configuration import Configuration
from entries.user import User
from entries.hostname import Hostname
from entries.model import Model
from entries.kernel import Kernel
from entries.uptime import Uptime
from entries.window_manager import WindowManager
from entries.desktop_environment import DesktopEnvironment
from entries.shell import Shell
from entries.terminal import Terminal
from entries.packages import Packages
from entries.temperature import Temperature
from entries.cpu import CPU
from entries.gpu import GPU
from entries.ram import RAM
from entries.disk import Disk
from entries.lan_ip import LanIp
from entries.wan_ip import WanIp
from constants import COLOR_DICT

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


# ----------- Classes Index ----------- #

class Classes(Enum):
    User = {
        'class': User,
        'kwargs': {
            'not_detected': CONFIG.get('default_strings')['not_detected']
        }
    }
    Hostname = {'class': Hostname}
    Model = {'class': Model}
    Distro = {'class': Distro}
    Kernel = {'class': Kernel}
    Uptime = {'class': Uptime}
    WindowManager = {
        'class': WindowManager,
        'kwargs': {
            'processes': PROCESSES,
            'not_detected': CONFIG.get('default_strings')['not_detected'],
        }
    }
    DesktopEnvironment = {
        'class': DesktopEnvironment,
        'kwargs': {
            'processes': PROCESSES,
            'not_detected': CONFIG.get('default_strings')['not_detected'],
        }
    }
    Shell = {
        'class': Shell,
        'kwargs': {
            'not_detected': CONFIG.get('default_strings')['not_detected'],
        }
    }
    Terminal = {
        'class': Terminal,
        'not_detected': CONFIG.get('default_strings')['not_detected'],
        'use_unicode': CONFIG.get('colors_palette')['use_unicode'],
        'clear_color': COLOR_DICT['clear']
    }
    Packages = {
        'class': Packages,
        'kwargs': {
            'not_detected': CONFIG.get('default_strings')['not_detected']
        }
    }
    Temperature = {
        'class': Temperature,
        'kwargs': {
            'use_fahrenheit': CONFIG.get('temperature')['use_fahrenheit'],
            'char_before_unit': CONFIG.get('temperature')['char_before_unit'],
            'not_detected': CONFIG.get('default_strings')['not_detected']
        }
    }
    CPU = {'class': CPU}
    GPU = {
         'class': GPU,
         'kwargs': {
           'not_detected': CONFIG.get('default_strings')['not_detected']
         }
    }
    RAM = {'class': RAM}
    Disk = {'class': Disk}
    LAN_IP = {
        'class': LanIp,
        'kwargs': {
            'ip_max_count': CONFIG.get('ip_settings')['lan_ip_max_count'],
            'no_address': CONFIG.get('default_strings')['no_address']
        }
    }
    WAN_IP = {
        'class': WanIp,
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
