#!/usr/bin/env python3

"""
Archey main file.
It loads each entry as a different class coming from the `entries` module.
Logos are stored under the `logos` module.
"""

import os
import sys

from enum import Enum
from subprocess import check_output

from .output import Output
from .configuration import Configuration
from .constants import COLOR_DICT
from .entries.user import User as e_User
from .entries.hostname import Hostname as e_Hostname
from .entries.model import Model as e_Model
from .entries.distro import Distro as e_Distro
from .entries.kernel import Kernel as e_Kernel
from .entries.uptime import Uptime as e_Uptime
from .entries.window_manager import WindowManager as e_WindowManager
from .entries.desktop_environment import DesktopEnvironment as e_DesktopEnvironment
from .entries.shell import Shell as e_Shell
from .entries.terminal import Terminal as e_Terminal
from .entries.packages import Packages as e_Packages
from .entries.temperature import Temperature as e_Temperature
from .entries.cpu import CPU as e_CPU
from .entries.gpu import GPU as e_GPU
from .entries.ram import RAM as e_RAM
from .entries.disk import Disk as e_Disk
from .entries.lan_ip import LanIp as e_LanIp
from .entries.wan_ip import WanIp as e_WanIp

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

# ----------- Classes Index ----------- #

class Classes(Enum):
    """
    One more enumeration to store and declare each one of our entries.
    The string representation of keys will act as entries names.
    Values will be set under the `value` attribute of each class.
    """
    User = {
        'class': e_User,
        'kwargs': {
            'not_detected': CONFIG.get('default_strings')['not_detected']
        }
    }
    Hostname = {'class': e_Hostname}
    Model = {
        'class': e_Model,
        'kwargs': {
            'virtual_environment': CONFIG.get(
                'default_strings'
            )['virtual_environment'],
            'bare_metal_environment': CONFIG.get(
                'default_strings'
            )['bare_metal_environment'],
            'not_detected': CONFIG.get(
                'default_strings'
            )['not_detected'],
        }
    }
    Distro = {'class': e_Distro}
    Kernel = {'class': e_Kernel}
    Uptime = {'class': e_Uptime}
    WindowManager = {
        'class': e_WindowManager,
        'kwargs': {
            'processes': PROCESSES,
            'not_detected': CONFIG.get('default_strings')['not_detected'],
        }
    }
    DesktopEnvironment = {
        'class': e_DesktopEnvironment,
        'kwargs': {
            'processes': PROCESSES,
            'not_detected': CONFIG.get('default_strings')['not_detected'],
        }
    }
    Shell = {
        'class': e_Shell,
        'kwargs': {
            'not_detected': CONFIG.get('default_strings')['not_detected'],
        }
    }
    Terminal = {
        'class': e_Terminal,
        'not_detected': CONFIG.get('default_strings')['not_detected'],
        'use_unicode': CONFIG.get('colors_palette')['use_unicode'],
        'clear_color': COLOR_DICT['clear']
    }
    Packages = {
        'class': e_Packages,
        'kwargs': {
            'not_detected': CONFIG.get('default_strings')['not_detected']
        }
    }
    Temperature = {
        'class': e_Temperature,
        'kwargs': {
            'use_fahrenheit': CONFIG.get('temperature')['use_fahrenheit'],
            'char_before_unit': CONFIG.get('temperature')['char_before_unit'],
            'not_detected': CONFIG.get('default_strings')['not_detected']
        }
    }
    CPU = {'class': e_CPU}
    GPU = {
        'class': e_GPU,
        'kwargs': {
            'not_detected': CONFIG.get('default_strings')['not_detected']
        }
    }
    RAM = {
        'class': e_RAM,
        'kwargs': {
            'sensor_color': COLOR_DICT['sensors'],
            'clear_color': COLOR_DICT['clear']
        }
    }
    Disk = {
        'class': e_Disk,
        'kwargs': {
            'sensor_color': COLOR_DICT['sensors'],
            'clear_color': COLOR_DICT['clear']
        }
    }
    LAN_IP = {
        'class': e_LanIp,
        'kwargs': {
            'ip_max_count': CONFIG.get('ip_settings')['lan_ip_max_count'],
            'no_address': CONFIG.get('default_strings')['no_address']
        }
    }
    WAN_IP = {
        'class': e_WanIp,
        'kwargs': {
            'ipv6_support': CONFIG.get('ip_settings')['wan_ip_v6_support'],
            'ipv6_timeout': CONFIG.get('timeout')['ipv6_detection'],
            'ipv4_timeout': CONFIG.get('timeout')['ipv4_detection'],
            'no_address': CONFIG.get('default_strings')['no_address']
        }
    }


# ---------------- Main --------------- #

def main():
    """Simple entry point"""
    output = Output()
    for key in Classes:
        if CONFIG.get('entries', {}).get(key.name, True):
            kwargs = key.value.get('kwargs', {})
            value = key.value['class'](**kwargs).value
            output.append(key.name, value)

    output.output()


if __name__ == '__main__':
    main()
