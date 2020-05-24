#!/usr/bin/env python3

"""
Archey main file.
It loads each entry as a different class coming from the `entries` module.
Logos are stored under the `logos` module.
"""

import argparse
import os

from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack

from archey._version import __version__
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


def args_parsing():
    """Simple wrapper to `argparse`"""
    parser = argparse.ArgumentParser(prog='archey')
    parser.add_argument(
        '-j', '--json',
        action='count',
        help='output entries data to JSON format, use multiple times to increase indentation'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=__version__
    )
    return parser.parse_args()


def main():
    """Simple entry point"""
    args = args_parsing()

    # `Processes` is a singleton, let's populate the internal list here.
    Processes()

    # `Configuration` is a singleton, let's populate the internal object here.
    configuration = Configuration()

    # From configuration, gather the entries user-enabled.
    enabled_entries = [
        (entry.value, entry.name)
        for entry in Entries
        if configuration.get('entries', {}).get(entry.name, True)
    ]

    output = Output(
        format_to_json=args.json
    )

    # We will map this function onto our enabled entries to instantiate them.
    def _entry_instantiator(entry_tuple):
        return entry_tuple[0](name=entry_tuple[1])

    # Let's use a context manager stack to manage conditional use of `TheadPoolExecutor`.
    with ExitStack() as cm_stack:
        if not configuration.get('parallel_loading'):
            mapper = map
        else:
            # Instantiate a threads pool to load our enabled entries in parallel.
            # We use threads (and not processes) since most work done by our entries is IO-bound.
            # Note: For Python < 3.5, we manually compute `max_workers`.
            # See <https://github.com/python/cpython/blob/3.5/Lib/concurrent/futures/thread.py#L94>.
            executor = cm_stack.enter_context(
                ThreadPoolExecutor(max_workers=((os.cpu_count() or 1) * 5))
            )
            mapper = executor.map

        for entry_instance in mapper(_entry_instantiator, enabled_entries):
            output.add_entry(entry_instance)

    output.output()


if __name__ == '__main__':
    main()
