"""Test module for Archey's device's model detection module"""

from subprocess import CalledProcessError

import unittest
from unittest.mock import MagicMock, mock_open, patch

from archey.entries.model import Model


class TestModelEntry(unittest.TestCase):
    """
    For this test we have to go through the three possibilities :
    * Laptop / Desktop "regular" environments
    * Raspberry Pi
    * Virtual environment (as a VM or a container)
    """
    def setUp(self):
        self._return_values = None

    @patch(
        'archey.entries.model.check_output',
        side_effect=CalledProcessError(1, 'systemd-detect-virt', "none\n")
    )
    @patch(
        'archey.entries.model.open',
        mock_open(read_data='MY-LAPTOP-MODEL\n'),
        create=True
    )
    def test_regular(self, _):
        """Sometimes, it could be quite simple..."""
        self.assertEqual(Model().value, 'MY-LAPTOP-MODEL')

    @patch(
        'archey.entries.model.check_output',
        side_effect=CalledProcessError(1, 'systemd-detect-virt', "none\n")
    )
    def test_raspberry(self, _):
        """Test for a typical Raspberry context"""
        with patch('archey.entries.model.open', mock_open(), create=True) as mock:
            mock.return_value.read.side_effect = [
                FileNotFoundError(),  # First `open` call will  (`/sys/[...]/product_name`)
                'Hardware\t: HARDWARE\nRevision\t: REVISION\n'
            ]

            self.assertEqual(
                Model().value,
                'Raspberry Pi HARDWARE (Rev. REVISION)'
            )

    @patch(
        'archey.entries.model.os.getuid',
        return_value=0
    )
    @patch(
        'archey.entries.model.check_output',
        side_effect=[
            FileNotFoundError(),  # `systemd-detect-virt` is not available
            'xen\nxen-domU\n',    # `virt-what` example output
            'MY-LAPTOP-MODEL\n'   # `dmidecode` example output
        ]
    )
    def test_virtual_environment(self, _, __):
        """Test for virtual machine"""
        self.assertEqual(
            Model().value,
            'MY-LAPTOP-MODEL (xen, xen-domU)'
        )

    @patch(
        'archey.entries.model.os.getuid',
        return_value=0
    )
    @patch(
        'archey.entries.model.check_output',
        side_effect=[
            FileNotFoundError(),  # `systemd-detect-virt` is not available
            'xen\nxen-domU\n',    # `virt-what` example output
            FileNotFoundError()   # `dmidecode` call will fail
        ]
    )
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'virtual_environment': 'Virtual Environment'}
    )
    def test_virtual_environment_without_dmidecode(self, _, __, ___):
        """Test for virtual machine (with a failing `dmidecode` call)"""
        self.assertEqual(
            Model().value,
            'Virtual Environment (xen, xen-domU)'
        )

    @patch(
        'archey.entries.model.os.getuid',
        return_value=1000
    )
    @patch(
        'archey.entries.model.check_output',
        return_value='systemd-nspawn\n'  # `systemd-detect-virt` example output
    )
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'virtual_environment': 'Virtual Environment'}
    )
    def test_virtual_environment_systemd_alone(self, _, __, ___):
        """Test for virtual environments, with systemd tools and `dmidecode`"""
        self.assertEqual(Model().value, 'Virtual Environment (systemd-nspawn)')

    @patch(
        'archey.entries.model.os.getuid',
        return_value=0
    )
    @patch(
        'archey.entries.model.check_output',
        side_effect=[
            'systemd-nspawn\n',  # `systemd-detect-virt` example output
            'MY-LAPTOP-MODEL\n'  # `dmidecode` example output
        ]
    )
    def test_virtual_environment_systemd_and_dmidecode(self, _, __):
        """Test for virtual environments, with systemd tools and `dmidecode`"""
        self.assertEqual(Model().value, 'MY-LAPTOP-MODEL (systemd-nspawn)')

    @patch(
        'archey.entries.model.os.getuid',
        return_value=1000
    )
    @patch(
        'archey.entries.model.check_output',
        side_effect=FileNotFoundError()
    )
    @patch(
        'archey.configuration.Configuration.get',
        return_value={'not_detected': 'Not detected'}
    )
    def test_no_match(self, _, __, ___):
        """Test when no information could be retrieved"""
        with patch('archey.entries.model.open', mock_open(), create=True) as mock:
            mock.return_value.read.side_effect = [
                FileNotFoundError(),      # First `open` call will  (`/sys/[...]/product_name`)
                'Hardware\t: HARDWARE\n'  # `Revision` entry is not present (`/proc/cpuinfo`)
            ]

            model = Model()

            output_mock = MagicMock()
            model.output(output_mock)

            self.assertIsNone(model.value)
            self.assertEqual(
                output_mock.append.call_args[0][1],
                'Not detected'
            )


if __name__ == '__main__':
    unittest.main()
