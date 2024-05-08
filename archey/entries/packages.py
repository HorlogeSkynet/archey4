"""Number of installed packages detection class"""

import os
import typing
from contextlib import suppress
from subprocess import DEVNULL, CalledProcessError, check_output

from archey.distributions import Distributions
from archey.entry import Entry


def get_homebrew_cellar_path() -> str:
    """Return Homebrew Cellar path (if available)"""
    with suppress(OSError, CalledProcessError):
        return check_output(["brew", "--cellar"], stderr=DEVNULL, universal_newlines=True).rstrip()

    return "/usr/local/Cellar/"


PACKAGES_TOOLS = (
    {"tool": "apk", "cmd": ("apk", "list", "--installed")},
    # As of 2020, `apt` is _very_ slow compared to `dpkg` on Debian-based distributions.
    # Additional note : `apt`'s CLI is currently not "stable" in Debian terms.
    # If `apt` happens to be preferred over `dpkg` in the future, don't forget to remove the latter.
    # {"cmd": ("apt", "list", "-qq", "--installed")},
    {"tool": "dnf", "cmd": ("dnf", "list", "installed"), "skew": 1},
    {"tool": "dpkg", "cmd": ("dpkg", "--get-selections")},
    {"tool": "emerge", "cmd": ("emerge", "-ep", "world"), "skew": 5},
    {"tool": "homebrew", "cmd": ("ls", "-1", get_homebrew_cellar_path())},  # Homebrew.
    {"tool": "nix-env", "cmd": ("nix-env", "-q")},
    {"tool": "pacman", "cmd": ("pacman", "-Q")},
    {"tool": "pacstall", "cmd": ("pacstall", "-L")},
    {"tool": "pkg_info", "cmd": ("pkg_info", "-a")},
    {
        "tool": "pkg",
        "cmd": ("pkg", "-N", "info", "-a"),
        # Query `pkg` only on *BSD systems to avoid inconsistencies.
        "only_on": (Distributions.FREEBSD, Distributions.NETBSD, Distributions.OPENBSD),
    },
    {"tool": "pkgin", "cmd": ("pkgin", "list")},
    {"tool": "port", "cmd": ("port", "installed"), "skew": 1},
    {"tool": "rpm", "cmd": ("rpm", "-qa")},
    {"tool": "slackware", "cmd": ("ls", "-1", "/var/log/packages/")},  # SlackWare.
    {"tool": "yum", "cmd": ("yum", "list", "installed"), "skew": 2},
    {"tool": "zypper", "cmd": ("zypper", "search", "-i"), "skew": 5},
)


class Packages(Entry):
    """Relies on the first found packages manager to list the installed packages"""

    _ICON = "\ueb29"  # cod_package

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for packages_tool in PACKAGES_TOOLS:
            packages_tool = typing.cast(dict, packages_tool)
            if (
                "only_on" in packages_tool
                and Distributions.get_local() not in packages_tool["only_on"]
            ):
                continue

            try:
                results = check_output(
                    packages_tool["cmd"],
                    stderr=DEVNULL,
                    env={
                        # Honor current process environment variables as some package managers
                        #  require an extended `PATH`.
                        **os.environ,
                        "LANG": "C",
                    },
                    universal_newlines=True,
                )
            except (OSError, CalledProcessError):
                continue
            
            count = results.count("\n")
            if count == 0:
                continue

            # If any, deduct output skew present due to the packages tool itself.
            if "skew" in packages_tool:
                count -= packages_tool["skew"]

            # For DPKG only, remove any not purged package.
            if packages_tool["tool"] == "dpkg":
                count -= results.count("deinstall")

            # Here we *may* use `\n` as `universal_newlines` has been set.
            if self.value:
                self.value += ", (" + packages_tool["tool"] + ") " + str(count)
            else:
                self.value = "(" + packages_tool["tool"] + ") " + str(count)

            # Let's just loop over, in case there are multiple package managers.
