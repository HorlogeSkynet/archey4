"""Test module for Archey's installed system packages detection module"""

import unittest
from unittest.mock import patch

from archey.entries.packages import Packages
from archey.configuration import Configuration
from archey.singleton import Singleton
import archey.default_configuration as DefaultConfig


class TestPackagesEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` calls and check afterwards
      that the outputs are correct.
    Sorry for the code style, mocking this class is pretty boring.
    """

    def setUp(self):
        """Runs when each test begins"""
        # Set up a default configuration instance.
        config = Configuration()
        config._config = DefaultConfig.CONFIGURATION # pylint: disable=protected-access

    def tearDown(self):
        """Runs when each test finishes testing"""
        # Destroy the singleton configuration instance (if created)
        try:
            del Singleton._instances[Configuration] # pylint: disable=protected-access
        except KeyError:
            pass

    @patch(
        'archey.entries.packages.check_output',
        return_value="""\
accountsservice/stable,now 0.6.45-2 amd64 [installed,automatic]
acl/stable,now 2.2.53-4 amd64 [installed,automatic]
adb/stable,now 1:8.1.0+r23-5 amd64 [installed]
adduser/stable,now 3.118 all [installed]
adwaita-icon-theme/stable,now 3.30.1-1 all [installed,automatic]
albatross-gtk-theme/stable,now 1.7.4-1 all [installed,automatic]
alsa-utils/stable,now 1.1.8-2 amd64 [installed,automatic]
""")
    def test_match_with_apt(self, _):
        """[Entry] [Packages] Simple test for the APT packages manager"""
        self.assertEqual(Packages().value, 7)

    @patch(
        'archey.entries.packages.check_output',
        side_effect=[
            FileNotFoundError(),
            """\
Installed Packages
GConf2.x86_64                  3.2.6-17.fc26           @@commandline
GeoIP.x86_64                   1.6.11-1.fc26           @@commandline
GeoIP-GeoLite-data.noarch      2017.07-1.fc26          @@commandline
GraphicsMagick.x86_64          1.3.26-3.fc26           @@commandline
"""])
    def test_match_with_dnf(self, _):
        """[Entry] [Packages] Simple test for the DNF packages manager"""
        self.assertEqual(Packages().value, 4)

    @patch(
        'archey.entries.packages.check_output',
        side_effect=[
            FileNotFoundError(),
            FileNotFoundError(),
            """\
accountsservice         install
acl                     install
adb                     install
adduser                 install
adwaita-icon-theme      install
albatross-gtk-theme     deinstall
alien                   install
"""])
    def test_match_with_dpkg(self, _):
        """[Entry] [Packages] Simple test for the DPKG packages manager"""
        self.assertEqual(Packages().value, 6)

    @patch(
        'archey.entries.packages.check_output',
        side_effect=[
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            """\

These are the packages that would be merged, in order:

Calculating dependencies  ... done!
[ebuild     U  ] sys-libs/glibc-2.25-r10 [2.25-r9]
[ebuild   R    ] sys-apps/busybox-1.28.0 \n\
[ebuild  N     ] sys-libs/libcap-2.24-r2  \
USE="pam -static-libs" ABI_X86="(64) -32 (-x32)" \n\
[ebuild     U  ] app-misc/pax-utils-1.2.2-r2 [1.1.7]
[ebuild   R    ] x11-misc/shared-mime-info-1.9 \n\

"""])
    def test_match_with_emerge(self, _):
        """[Entry] [Packages] Simple test for the Emerge packages manager"""
        self.assertEqual(Packages().value, 5)

    @patch(
        'archey.entries.packages.check_output',
        side_effect=[
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            """\
acl 2.2.52-4
archey4 v4.3.3-1
archlinux-keyring 20180108-1
argon2 20171227-3
"""])
    def test_match_with_pacman(self, _):
        """[Entry] [Packages] Simple test for the Pacman packages manager"""
        self.assertEqual(Packages().value, 4)

    @patch(
        'archey.entries.packages.check_output',
        side_effect=[
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            """\
cdrecord-2.01-10.7.el5
bluez-libs-3.7-1.1
setarch-2.0-1.1
MySQL-client-3.23.57-1
"""])
    def test_match_with_rpm(self, _):
        """[Entry] [Packages] Simple test for the RPM packages manager"""
        self.assertEqual(Packages().value, 4)

    @patch(
        'archey.entries.packages.check_output',
        side_effect=[
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            """\
Loaded plugins: fastestmirror, langpacks
Installed Packages
GConf2.x86_64                   3.2.6-8.el7         @base/$releasever
GeoIP.x86_64                    1.5.0-11.el7        @base            \n\
ModemManager.x86_64             1.6.0-2.el7         @base            \n\
ModemManager-glib.x86_64        1.6.0-2.el7         @base            \n\
"""])
    def test_match_with_yum(self, _):
        """[Entry] [Packages] Simple test for the Yum packages manager"""
        self.assertEqual(Packages().value, 4)

    @patch(
        'archey.entries.packages.check_output',
        side_effect=[
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            """\
Loading repository data...
Reading installed packages...

S  | Name          | Summary                             | Type       \n\
---+---------------+-------------------------------------+------------
i+ | 5201          | Recommended update for xdg-utils    | patch      \n\
i  | GeoIP-data    | Free GeoLite country-data for GeoIP | package    \n\
i  | make          | GNU make                            | package    \n\
i  | GNOME Nibbles | Guide a worm around a maze          | application
i  | at            | A Job Manager                       | package    \n\
"""])
    def test_match_with_zypper(self, _):
        """[Entry] [Packages] Simple test for the Zypper packages manager"""
        self.assertEqual(Packages().value, 5)

    @patch(
        'archey.entries.packages.check_output',
        side_effect=[  # No packages manager will be found
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError(),
            FileNotFoundError()
        ]
    )
    @patch.dict(
        Configuration()._config, # pylint: disable=protected-access
        {
            'default_strings': {
                'not_detected': 'Not detected'
            }
        }
    )
    def test_no_packages_manager(self, _):
        """[Entry] [Packages] No packages manager is available at the moment..."""
        self.assertEqual(Packages().value, 'Not detected')


if __name__ == '__main__':
    unittest.main()
