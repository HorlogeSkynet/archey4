"""Test module for `archey.processes`"""

import unittest
from unittest.mock import patch

from archey.processes import Processes


# To avoid edge-case issues due to singleton, we automatically reset internal `_instances`.
# This is done at the class-level.
@patch.dict(
    'archey.singleton.Singleton._instances',
    clear=True
)
class TestProcessesUtil(unittest.TestCase):
    """
    Test cases for the `Processes` (singleton) class.
    To work around the singleton, we reset the internal `_instances` dictionary.
    This way, `check_output` can be mocked here.
    """
    @patch(
        'archey.processes.check_output',
        return_value="""\
COMMAND
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

        self.assertTupleEqual(
            processes_1.list,
            ('what', 'an', 'awesome', 'processes', 'list', 'you', 'got', 'there')
        )
        self.assertEqual(processes_1.number, 8)

        # The class has been instantiated twice, but `check_output` has been called only once.
        # `unittest.mock.Mock.assert_called_once` is not available against Python < 3.6.
        self.assertEqual(check_output_mock.call_count, 1)

    @patch(
        'archey.processes.check_output',
        side_effect=FileNotFoundError()
    )
    @patch(
        'archey.processes.print',
        return_value=None  # Let's nastily mute class' outputs.
    )
    def test_ps_not_available(self, _, __):
        """Verifies that the program stops when `ps` is not available"""
        self.assertRaises(SystemExit, Processes)


if __name__ == '__main__':
    unittest.main()
