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
from archey.distributions import Distributions
from archey.processes import Processes
from archey.screenshot import take_screenshot
from archey.entries.user import User as e_User
from archey.entries.hostname import Hostname as e_Hostname
from archey.entries.model import Model as e_Model
from archey.entries.distro import Distro as e_Distro
from archey.entries.kernel import Kernel as e_Kernel
from archey.entries.uptime import Uptime as e_Uptime
from archey.entries.processes import Processes as e_Processes
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
    Processes = e_Processes
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
        '-c', '--config-path',
        metavar='PATH',
        help='path to a configuration file, or a directory containing a `config.json`'
    )
    parser.add_argument(
        '-d', '--distribution',
        metavar='IDENTIFIER',
        choices=Distributions.get_distribution_identifiers(),
        help='supported distribution identifier to show the logo of, pass `unknown` to list them'
    )
    parser.add_argument(
        '-j', '--json',
        action='count',
        help='output entries data to JSON format, use multiple times to increase indentation'
    )
    parser.add_argument(
        '-s', '--screenshot',
        metavar='PATH',
        nargs='?',
        const=False,
        help='take a screenshot once execution is done, optionally specify a target path'
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
    configuration = Configuration(config_path=args.config_path)

    # From configuration, gather the entries user-enabled.
    enabled_entries = [
        (entry.value, entry.name)
        for entry in Entries
        if configuration.get('entries', {}).get(entry.name, True)
    ]

    output = Output(
        preferred_distribution=args.distribution,
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
            # `max_workers` is manually computed to mimic Python 3.8+ behaviour, but for our needs.
            #   See <https://github.com/python/cpython/pull/13618>.
            executor = cm_stack.enter_context(ThreadPoolExecutor(
                max_workers=min(len(enabled_entries) or 1, (os.cpu_count() or 1) + 4)
            ))
            mapper = executor.map

        for entry_instance in mapper(_entry_instantiator, enabled_entries):
            output.add_entry(entry_instance)

    output.output()

    # Has the screenshot flag been specified ?
    if args.screenshot is not None:
        # If so, but still _falsy_, pass `None` as no output file has been specified by the user.
        take_screenshot((args.screenshot or None))


if __name__ == '__main__':
    main()
