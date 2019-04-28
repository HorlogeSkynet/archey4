#!/usr/bin/env python3

"""
Archey main file.
It loads each entry as a different class coming from the `entries` module.
Logos are stored under the `logos` module.
"""

from enum import Enum

from .output import Output
from .configuration import Configuration
from .processes import Processes
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


class Classes(Enum):
    """
    An enumeration to store and declare each one of our entries.
    The string representation of keys will act as entries names.
    Values will be set under the `value` attribute of each obtained objects.
    """
    User = e_User
    Hostname = e_Hostname
    Model = e_Model
    Distro = e_Distro
    Kernel = e_Kernel
    Uptime = e_Uptime
    WindowManager = e_WindowManager
    DesktopEnvironment = e_DesktopEnvironment
    Shell = e_Shell
    Terminal = e_Terminal
    Packages = e_Packages
    Temperature = e_Temperature
    CPU = e_CPU
    GPU = e_GPU
    RAM = e_RAM
    Disk = e_Disk
    LAN_IP = e_LanIp
    WAN_IP = e_WanIp


def main():
    """Simple entry point"""

    # `Processes` is a singleton, let's populate the internal list here.
    Processes()

    # `Configuration` is a singleton, let's populate the internal object here.
    configuration = Configuration()

    output = Output()
    for key in Classes:
        if configuration.get('entries', {}).get(key.name, True):
            output.append(key.name, key.value().value)

    output.output()


if __name__ == '__main__':
    main()
