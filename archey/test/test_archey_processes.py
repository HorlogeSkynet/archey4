"""Test module for `archey.processes`"""

import unittest
from unittest.mock import patch

from archey.processes import Processes


class TestProcessesUtil(unittest.TestCase):
    """
    Test cases for the `Processes` (singleton) class.
    To work around the singleton, we reset the internal `_instances` dictionary.
    This way, `check_output` can be mocked here.
    """
    @patch.dict(
        'archey.singleton.Singleton._instances',
        clear=True
    )
    @patch(
        'archey.processes.check_output',
        return_value="""\
what
an
awesome
processes
list
you
got
there
""")
    def test_ps_ok(self, check_output_mock):
        """Simple test with a plausible `ps` output"""
        # We'll create two `Processes` instances.
        processes_1 = Processes()
        _ = Processes()

        self.assertEqual(
            processes_1.get(),
            ['what', 'an', 'awesome', 'processes', 'list', 'you', 'got', 'there']
        )

        # The class has been instantiated twice, but `check_output` has been called only once.
        # `unittest.mock.Mock.assert_called_once` is not available against Python < 3.6.
        self.assertEqual(check_output_mock.call_count, 1)

    @patch.dict(
        'archey.singleton.Singleton._instances',
        clear=True
    )
    @patch(
        'archey.processes.check_output',
        side_effect=FileNotFoundError()
    )
    def test_ps_not_available(self, _):
        """Verifies that the program stops when `ps` is not available"""
        self.assertRaises(SystemExit, Processes)


if __name__ == '__main__':
    unittest.main()
