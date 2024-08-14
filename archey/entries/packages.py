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


PACKAGES_TOOLS: typing.Tuple[typing.Dict[str, typing.Any], ...] = (
    {"cmd": ("apk", "list", "--installed")},
    # As of 2020, `apt` is _very_ slow compared to `dpkg` on Debian-based distributions.
    # Additional note : `apt`'s CLI is currently not "stable" in Debian terms.
    # If `apt` happens to be preferred over `dpkg` in the future, don't forget to remove the latter.
    # {"cmd": ("apt", "list", "-qq", "--installed")},
    {"cmd": ("dnf", "list", "installed"), "skew": 1},
    {"cmd": ("dpkg", "--get-selections")},
    {"cmd": ("emerge", "-ep", "world"), "skew": 5},
    {"cmd": ("flatpak", "list"), "skew": 1},
    {"cmd": ("ls", "-1", get_homebrew_cellar_path()), "name": "homebrew"},
    {"cmd": ("nix-env", "-q")},
    {"cmd": ("pacman", "-Q")},
    {"cmd": ("pacstall", "-L")},
    {"cmd": ("pkg_info", "-a")},
    {
        "cmd": ("pkg", "-N", "info", "-a"),
        # Query `pkg` only on *BSD systems to avoid inconsistencies.
        "only_on": (Distributions.FREEBSD, Distributions.NETBSD, Distributions.OPENBSD),
    },
    {"cmd": ("pkgin", "list")},
    {"cmd": ("port", "installed"), "skew": 1},
    {"cmd": ("rpm", "-qa")},
    {"cmd": ("ls", "-1", "/var/log/packages/"), "name": "slackware"},
    {"cmd": ("snap", "list", "--all"), "skew": 1},
    {"cmd": ("yum", "list", "installed"), "skew": 2},
    {"cmd": ("zypper", "search", "-i"), "skew": 5},
)


class Packages(Entry):
    """Relies on the first found packages manager to list the installed packages"""

    _ICON = "\ueb29"  # cod_package

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = {}

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

            # Here we *may* use `\n` as `universal_newlines` has been set.
            count = results.count("\n")

            # If any, deduct output skew present due to the packages tool itself.
            if "skew" in packages_tool:
                count -= packages_tool["skew"]

            pkg_tool_name = packages_tool.get("name", packages_tool["cmd"][0])

            # For DPKG only, remove any not purged package.
            if pkg_tool_name == "dpkg":
                count -= results.count("deinstall")

            self.value[pkg_tool_name] = count

    def output(self, output) -> None:
        """Adds the entry to `output` after pretty-formatting packages tool counts"""
        if not self.value:
            # Fall back on the default behavior if no temperatures were detected.
            super().output(output)
            return

        if self.options.get("combine_total"):
            output.append(self.name, str(sum(self.value.values())))
            return

        entries = []
        for pkg_tool_name, count in self.value.items():
            if count > 0 or self.options.get("show_zeros"):
                entries.append(f"({pkg_tool_name}) {count}")

        if self.options.get("one_line", True):
            # One-line output is enabled : Join the results !
            output.append(self.name, ", ".join(entries))
        else:
            # One-line output has been disabled, add one entry per item.
            for entry in entries:
                output.append(self.name, entry)
