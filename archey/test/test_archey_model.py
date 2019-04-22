"""Test module for Archey's device's model detection module"""

import unittest
from unittest.mock import mock_open, patch

from archey.entries.model import Model


class TestModelEntry(unittest.TestCase):
    """
    For this test we have to go through the three possibilities :
    * Laptop / Desktop "regular" environments
    * Raspberry Pi
    * Virtual environment (as a VPS or a VM)
    """

    def setUp(self):
        self.return_values = None

    @patch(
        'archey.entries.model.open',
        mock_open(
            read_data='MY-LAPTOP-MODEL\n'
        ),
        create=True
    )
    def test_regular(self):
        """Sometimes, it could be quite simple..."""
        self.assertEqual(
            Model(None, None, None).value,
            'MY-LAPTOP-MODEL'
        )

    def test_raspberry(self):
        """Test for a typical Raspberry context"""
        self.return_values = [
            FileNotFoundError(),  # First `open` call will fail
            'Hardware\t: HARDWARE\nRevision\t: REVISION\n'
        ]

        with patch('archey.entries.model.open', mock_open(), create=True) as mock:
            mock.return_value.read.side_effect = self._special_func_for_mock_open
            self.assertEqual(
                Model(None, None, None).value,
                'Raspberry Pi HARDWARE (Rev. REVISION)'
            )

    @patch(
        'archey.entries.model.check_output',
        side_effect=[
            'xen\nxen-domU',     # `virt-what` output example
            'MY-LAPTOP-MODEL\n'  # `dmidecode` output example
        ]
    )
    def test_virtual_environment(self, _):
        """Test for virtual machine"""
        self.return_values = [
            FileNotFoundError(),      # First `open` call will fail
            'Hardware\t: HARDWARE\n'  # `Revision` entry is not present
        ]

        with patch('archey.entries.model.open', mock_open(), create=True) as mock:
            mock.return_value.read.side_effect = self._special_func_for_mock_open
            self.assertEqual(
                Model(None, None, None).value,
                'MY-LAPTOP-MODEL (xen, xen-domU)'
            )

    @patch(
        'archey.entries.model.check_output',
        side_effect=[
            'xen\nxen-domU',     # `virt-what` output example
            FileNotFoundError()  # `dmidecode` call will fail
        ]
    )
    def test_virtual_environment_without_dmidecode(self, _):
        """Test for virtual machine (with a failing `dmidecode` call)"""
        self.return_values = [
            FileNotFoundError(),      # First `open` call will fail
            'Hardware\t: HARDWARE\n'  # `Revision` entry is not present
        ]

        with patch('archey.entries.model.open', mock_open(), create=True) as mock:
            mock.return_value.read.side_effect = self._special_func_for_mock_open
            self.assertEqual(
                Model('Virtual Environment', None, None).value,
                'Virtual Environment (xen, xen-domU)'
            )

    @patch(
        'archey.entries.model.check_output',
        return_value="""\
\
""")
    def test_bare_metal(self, _):
        """Test for "bare-metal" devices, with no further information"""
        self.return_values = [
            FileNotFoundError(),      # First `open` call will fail
            'Hardware\t: HARDWARE\n'  # `Revision` entry is not present
        ]

        with patch('archey.entries.model.open', mock_open(), create=True) as mock:
            mock.return_value.read.side_effect = self._special_func_for_mock_open
            self.assertEqual(
                Model(None, 'Bare-metal Environment', None).value,
                'Bare-metal Environment'
            )

    @patch(
        'archey.entries.model.check_output',
        side_effect=FileNotFoundError()
    )
    def test_no_match(self, _):
        """Test when no information could be retrieved"""
        self.return_values = [
            FileNotFoundError(),      # First `open` call will fail
            'Hardware\t: HARDWARE\n'  # `Revision` entry is not present
        ]

        with patch('archey.entries.model.open', mock_open(), create=True) as mock:
            mock.return_value.read.side_effect = self._special_func_for_mock_open
            self.assertEqual(
                Model(None, None, 'Not detected').value,
                'Not detected'
            )

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
