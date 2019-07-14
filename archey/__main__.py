#!/usr/bin/env python3

"""
Archey main file.
It loads each entry as a different class coming from the `entries` module.
Logos are stored under the `logos` module.
"""

from enum import Enum

from archey.output import Output
from archey.configuration import Configuration
from archey.processes import Processes
from archey.entries.user import User as e_User
from archey.entries.hostname import Hostname as e_Hostname
from archey.entries.model import Model as e_Model
from archey.entries.distro import Distro as e_Distro
from archey.entries.kernel import Kernel as e_Kernel
from archey.entries.uptime import Uptime as e_Uptime
from archey.entries.window_manager import WindowManager as e_WindowManager
from archey.entries.desktop_environment import DesktopEnvironment as e_DesktopEnvironment
from archey.entries.shell import Shell as e_Shell
from archey.entries.terminal import Terminal as e_Terminal
from archey.entries.packages import Packages as e_Packages
from archey.entries.temperature import Temperature as e_Temperature
from archey.entries.cpu import CPU as e_CPU
from archey.entries.gpu import GPU as e_GPU
from archey.entries.ram import RAM as e_RAM
from archey.entries.disk import Disk as e_Disk
from archey.entries.lan_ip import LanIp as e_LanIp
from archey.entries.wan_ip import WanIp as e_WanIp


class Entries(Enum):
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
    for entry in Entries:
        if configuration.get('entries', {}).get(entry.name, True):
            output.append(entry.name, entry.value().value)

    output.output()


if __name__ == '__main__':
    main()
