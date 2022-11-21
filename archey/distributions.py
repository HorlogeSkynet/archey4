"""
Distributions enumeration module.
Operating Systems detection logic.
Interface to `os-release` (through `distro` module).
"""

import os
import platform
import sys
from contextlib import suppress
from enum import Enum
from functools import lru_cache
from typing import List, Optional

import distro


class Distributions(Enum):
    """
    This enumeration lists supported operating systems (keys).
    Values contain their respective `distro` identifier.
    See <https://distro.readthedocs.io/en/latest/#distro.id>.
    """

    ALPINE = "alpine"
    ANDROID = "android"
    ARCH = "arch"
    BUILDROOT = "buildroot"
    BUNSENLABS = "bunsenlabs"
    CENTOS = "centos"
    CRUNCHBANG = "crunchbang"
    DARWIN = "darwin"
    DEBIAN = "debian"
    DEVUAN = "devuan"
    ELEMENTARY = "elementary"
    ENSO = "enso"
    FEDORA = "fedora"
    FREEBSD = "freebsd"
    GENTOO = "gentoo"
    GUIX = "guix"
    KALI = "kali"
    MANJARO = "manjaro"
    MOEVALENT = "moevalent"
    NETBSD = "netbsd"
    NIXOS = "nixos"
    LINUX = "linux"
    LINUXMINT = "linuxmint"
    OPENBSD = "openbsd"
    OPENSUSE = "opensuse"
    POP = "pop"
    PARABOLA = "parabola"
    RASPBIAN = "raspbian"
    ROCKY = "rocky"
    RHEL = "rhel"
    SIDUCTION = "siduction"
    SLACKWARE = "slackware"
    UBUNTU = "ubuntu"
    UNIVALENT = "univalent"
    WINDOWS = "windows"

    @staticmethod
    def get_identifiers() -> List[str]:
        """Simple getter returning current supported distributions identifiers"""
        return [d.value for d in Distributions.__members__.values()]

    @staticmethod
    @lru_cache(maxsize=None)  # Python < 3.9, `functools.cache` is not yet available.
    def get_local() -> "Distributions":
        """Entry point of Archey distribution detection logic"""
        distribution = Distributions._vendor_detection()

        # In case nothing got detected the "regular" way...
        if not distribution:
            # Are we running on Darwin (somehow not previously detected by `distro`) ?
            if platform.system() == "Darwin":
                return Distributions.DARWIN

            # Android systems are currently not being handled by `distro`.
            # At first, we imitate the Python standard library, by checking whether CPython
            #  has been built for Android.
            #  See <https://github.com/python/cpython/search?l=Python&q=getandroidapilevel>
            # As a fallback, we mimic Neofetch behavior, by relying on the file-system.
            #  See <https://github.com/nir0s/distro/issues/253>
            if hasattr(sys, "getandroidapilevel") or (
                os.path.isdir("/system/app") and os.path.isdir("/system/priv-app")
            ):
                return Distributions.ANDROID

            # If nothing of the above matched, fall-back on the Linux logo.
            return Distributions.LINUX

        # Below are brain-dead cases for distributions not properly handled by `distro`.
        # One _may_ want to add its own logic to add support for such undetectable systems.
        if distribution == Distributions.DEBIAN:
            # CrunchBang is tagged as _regular_ Debian by `distro`.
            # Below conditions are here to work-around this issue.
            # First condition : CrunchBang-Linux and CrunchBang-Monara.
            # Second condition : CrunchBang++ (CBPP).
            if os.path.isfile("/etc/lsb-release-crunchbang") or os.path.isfile(
                "/usr/bin/cbpp-exit"
            ):
                return Distributions.CRUNCHBANG

        elif distribution == Distributions.UBUNTU:
            # Older Pop!_OS releases (< 20.*) didn't ship their own `ID` (from `os-release`).
            # Thus, they are detected as "regular" Ubuntu distributions.
            # We may here rely on their `NAME` (from `os-release`), which is sufficient.
            if Distributions.get_distro_name(pretty=False) == "Pop!_OS":
                return Distributions.POP

        return distribution

    @staticmethod
    def _vendor_detection() -> Optional["Distributions"]:
        """Main distribution detection logic, relying on `distro`, handling _common_ cases"""
        # Are we running on Windows ?
        if platform.system() == "Windows":
            return Distributions.WINDOWS

        # Is `ID` (from `os-release`) well-known and supported ?
        with suppress(ValueError):
            return Distributions(distro.id())

        # Is any of `ID_LIKE` (from `os-release`) well-known and supported ?
        # See <https://www.freedesktop.org/software/systemd/man/os-release.html#ID_LIKE=>.
        for id_like in distro.like().split(" "):
            with suppress(ValueError):
                return Distributions(id_like)

        # Nothing of the above matched, let's return `None` and let the caller handle it.
        return None

    @staticmethod
    def get_distro_name(pretty: bool = True) -> Optional[str]:
        """Simple wrapper to `distro` to return the current distribution _pretty_ name"""
        return distro.name(pretty=pretty) or None

    @staticmethod
    def get_ansi_color() -> Optional[str]:
        """
        Simple wrapper to `distro` to return the distribution preferred ANSI color.
        See <https://www.freedesktop.org/software/systemd/man/os-release.html#ANSI_COLOR=>.
        """
        return distro.os_release_attr("ansi_color") or None
