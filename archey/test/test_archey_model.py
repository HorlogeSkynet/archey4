"""Test module for Archey's device's model detection module"""

import unittest
from unittest.mock import mock_open, patch

from archey.entries.model import Model


class TestModelEntry(unittest.TestCase):
    """
    For this test we have to go through the three possibilities :
    * Laptop / Desktop "regular" environments
    * Raspberry Pi
    * Virtual environment (as a VM or a container)
    """
    def setUp(self):
        self.return_values = None

    @patch(
        'archey.entries.model.check_output',
        return_value='none\n'
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
        return_value='none\n'
    )
    def test_raspberry(self, _):
        """Test for a typical Raspberry context"""
        self.return_values = [
            FileNotFoundError(),  # First `open` call will fail
            'Hardware\t: HARDWARE\nRevision\t: REVISION\n'
        ]

        with patch('archey.entries.model.open', mock_open(), create=True) as mock:
            mock.return_value.read.side_effect = self._special_func_for_mock_open
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
        'archey.entries.model.Configuration.get',
        return_value={
            'not_detected': 'Not detected',
            'virtual_environment': 'Virtual Environment'
        }
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
        'archey.entries.model.Configuration.get',
        return_value={
            'not_detected': 'Not detected',
            'virtual_environment': 'Virtual Environment'
        }
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
    @patch(
        'archey.entries.model.Configuration.get',
        return_value={
            'not_detected': 'Not detected',
            'virtual_environment': 'Virtual Environment'
        }
    )
    def test_virtual_environment_systemd_and_dmidecode(self, _, __, ___):
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
        'archey.entries.model.Configuration.get',
        return_value={
            'not_detected': 'Not detected',
            'virtual_environment': 'Virtual Environment'
        }
    )
    def test_no_match(self, _, __, ___):
        """Test when no information could be retrieved"""
        self.return_values = [
            FileNotFoundError(),      # First `open` call will fail
            'Hardware\t: HARDWARE\n'  # `Revision` entry is not present
        ]

        with patch('archey.entries.model.open', mock_open(), create=True) as mock:
            mock.return_value.read.side_effect = self._special_func_for_mock_open
            self.assertEqual(Model().value, 'Not detected')

    def _special_func_for_mock_open(self):
        """
        This method does not belong to the test cases.
        It's a special method which allows mocking multiple `io.open` calls.
        You just have to set the values within a list `self.return_values`.
        And then :
        `mock.return_value.read.side_effect = self._special_func_for_mock_open`
        """
        return_value = self.return_values.pop(0)

        # Either return value or raise any specified exception
        if issubclass(return_value.__class__, OSError().__class__):
            raise return_value

        return return_value


if __name__ == '__main__':
    unittest.main()
