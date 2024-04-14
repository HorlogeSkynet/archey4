"""Desktop environment detection class"""

import configparser
import os
import platform
import typing
from contextlib import suppress

from archey.entry import Entry
from archey.processes import Processes

DE_PROCESSES = {
    "cinnamon": "Cinnamon",
    "dde-dock": "Deepin",
    "fur-box-session": "Fur Box",
    "gnome-session": "GNOME",
    "gnome-shell": "GNOME",
    "ksmserver": "KDE",
    "lxqt-session": "LXQt",
    "lxsession": "LXDE",
    "mate-session": "MATE",
    "xfce4-session": "Xfce",
}

# From : <https://specifications.freedesktop.org/menu-spec/latest/apb.html>
XDG_DESKTOP_NORMALIZATION = {
    "DDE": "Deepin",
    "ENLIGHTENMENT": "Enlightenment",
    "GNOME-CLASSIC": "GNOME Classic",
    "GNOME-FLASHBACK": "GNOME Flashback",
    "RAZOR": "Razor-qt",
    "TDE": "Trinity",
    "X-CINNAMON": "Cinnamon",
}

# (partly) from : <https://wiki.archlinux.org/title/Xdg-utils#Environment_variables>
DE_NORMALIZATION = {
    "budgie-desktop": "Budgie",
    "cinnamon": "Cinnamon",
    "deepin": "Deepin",
    "enlightenment": "Enlightenment",
    "gnome": "Gnome",
    "kde": "KDE",
    "lumina": "Lumina",
    "lxde": "LXDE",
    "lxqt": "LXQt",
    "mate": "MATE",
    "muffin": "Cinnamon",
    "trinity": "Trinity",
    "xfce session": "Xfce",
    "xfce": "Xfce",
    "xfce4": "Xfce",
    "xfce5": "Xfce",
}


class DesktopEnvironment(Entry):
    """
    Return static values for macOS and Windows.
    On Linux, use extensive environment variables processing to find known identifiers.
    Fallback on running processes to find a known-entry.
    """

    _ICON = "\ue23c"  # fae_restore
    _PRETTY_NAME = "Desktop Environment"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = (
            self._platform_detection() or self._environment_detection() or self._process_detection()
        )

    @staticmethod
    def _platform_detection() -> typing.Optional[str]:
        # macOS' desktop environment is called "Aqua",
        #   and could not be detected from processes list.
        if platform.system() == "Darwin":
            return "Aqua"

        # Same thing for Windows, based on release version.
        if platform.system() == "Windows":
            windows_release = platform.win32_ver()[0]
            if windows_release in ("Vista", "7"):
                return "Aero"
            if windows_release in ("8", "10"):
                return "Metro"

        return None

    @staticmethod
    def _environment_detection() -> (
        typing.Optional[str]
    ):  # pylint: disable=too-many-return-statements
        """Implement same algorithm xdg-utils uses"""
        # Honor XDG_CURRENT_DESKTOP (if set)
        desktop_identifiers = os.getenv("XDG_CURRENT_DESKTOP", "").split(":")
        if desktop_identifiers[0]:
            return XDG_DESKTOP_NORMALIZATION.get(
                desktop_identifiers[0].upper(), desktop_identifiers[0]
            )

        # Honor known environment-specific variables
        if "GNOME_DESKTOP_SESSION_ID" in os.environ:
            return "GNOME"
        if "HYPRLAND_CMD" in os.environ:
            return "Hyprland"
        if "KDE_FULL_SESSION" in os.environ:
            return "KDE"
        if "MATE_DESKTOP_SESSION_ID" in os.environ:
            return "MATE"
        if "TDE_FULL_SESSION" in os.environ:
            return "Trinity"

        # Fallback to (known) "DE"/"DESKTOP_SESSION" legacy environment variables
        legacy_de = os.getenv("DE", "").lower()
        if legacy_de in DE_NORMALIZATION:
            return DE_NORMALIZATION[legacy_de]

        desktop_session = os.getenv("DESKTOP_SESSION")
        if desktop_session is not None:
            # If DESKTOP_SESSION corresponds to a session's desktop entry path, parse and honor it
            with suppress(ValueError, OSError, configparser.Error):
                desktop_file = os.path.realpath(desktop_session)
                if (
                    os.path.commonprefix([desktop_file, "/usr/share/xsessions"])
                    == "/usr/share/xsessions"
                ):
                    # Don't expect anything from .desktop files and parse them in a best-effort way
                    config = configparser.ConfigParser(allow_no_value=True, strict=False)
                    with open(desktop_file, encoding="utf-8") as f_desktop_file:
                        config.read_string(f_desktop_file.read())
                    return (
                        # Honor `DesktopNames` option with `X-LightDM-DesktopName` as a fallback
                        config.get("Desktop Entry", "DesktopNames", fallback=None)
                        or config.get("Desktop Entry", "X-LightDM-DesktopName")
                    ).split(";")[0]

            # If not or if file couldn't be read, check whether it corresponds to a known identifier
            if desktop_session.lower() in DE_NORMALIZATION:
                return DE_NORMALIZATION[desktop_session.lower()]

        return None

    @staticmethod
    def _process_detection() -> typing.Optional[str]:
        processes = Processes().list
        for de_id, de_name in DE_PROCESSES.items():
            if de_id in processes:
                return de_name

        return None
