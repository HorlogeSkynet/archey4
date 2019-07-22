"""Test module for Archey's kernel information detection module"""

import unittest
from unittest.mock import patch

from archey.entries.kernel import Kernel


class TestKernelEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call and check afterwards
      that the output is correct.
    """
    @patch(
        'archey.entries.kernel.check_output',
        return_value="""\
X.Y.Z-R-arch
""")
    def test(self, _):
        """A simple test, for a simple mock"""
        self.assertEqual(Kernel().value, 'X.Y.Z-R-arch')


if __name__ == '__main__':
    unittest.main()
