
import unittest
from unittest.mock import mock_open, patch

from archey.archey import Model


class TestModelEntry(unittest.TestCase):
    """
    For this test we have to go through the three possibilities :
    * Laptop / Desktop "regular" environments
    * Raspberry Pi
    * Virtual environment (as a VPS or a VM)
    """
    @patch(
        'archey.archey.open',
        mock_open(
            read_data='MY-LAPTOP-MODEL\n'
        ),
        create=True
    )
    def test_regular(self):
        self.assertEqual(Model().value, 'MY-LAPTOP-MODEL')

    def test_raspberry(self):
        self.return_values = [
            FileNotFoundError(),  # First `open` call will fail
            'Hardware\t: HARDWARE\nRevision\t: REVISION\n'
        ]

        with patch('archey.archey.open', mock_open(), create=True) as mock:
            mock.return_value.read.side_effect = \
                self._special_func_for_mock_open
            self.assertEqual(
                Model().value,
                'Raspberry Pi HARDWARE (Rev. REVISION)'
            )

    @patch(
        'archey.archey.check_output',
        side_effect=[
            'xen\nxen-domU',     # `virt-what` output example
            'MY-LAPTOP-MODEL\n'  # `dmidecode` output example
        ]
    )
    def test_virtual(self, check_output_mock):
        self.return_values = [
            FileNotFoundError(),      # First `open` call will fail
            'Hardware\t: HARDWARE\n'  # `Revision` entry is not present
        ]

        with patch('archey.archey.open', mock_open(), create=True) as mock:
            mock.return_value.read.side_effect = \
                self._special_func_for_mock_open
            self.assertEqual(
                Model().value,
                'MY-LAPTOP-MODEL (xen, xen-domU)'
            )

    @patch(
        'archey.archey.check_output',
        return_value='\n'
    )
    @patch.dict(
        'archey.archey.config.config',
        {
            'default_strings': {
                'bare_metal_environment': 'Bare-metal Environment'
            }
        }
    )
    def test_bare_metal(self, check_output_mock):
        self.return_values = [
            FileNotFoundError(),      # First `open` call will fail
            'Hardware\t: HARDWARE\n'  # `Revision` entry is not present
        ]

        with patch('archey.archey.open', mock_open(), create=True) as mock:
            mock.return_value.read.side_effect = \
                self._special_func_for_mock_open
            self.assertEqual(Model().value, 'Bare-metal Environment')

    @patch(
        'archey.archey.check_output',
        side_effect=FileNotFoundError()
    )
    @patch.dict(
        'archey.archey.config.config',
        {'default_strings': {'not_detected': 'Not detected'}}
    )
    def test_no_match(self, check_output_mock):
        self.return_values = [
            FileNotFoundError(),      # First `open` call will fail
            'Hardware\t: HARDWARE\n'  # `Revision` entry is not present
        ]

        with patch('archey.archey.open', mock_open(), create=True) as mock:
            mock.return_value.read.side_effect = \
                self._special_func_for_mock_open
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
        else:
            return return_value


if __name__ == '__main__':
    unittest.main()
