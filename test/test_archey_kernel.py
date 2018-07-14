#!/usr/bin/env python3

# pylint: disable=C0111, W0613


import unittest
from unittest.mock import patch

from archey.archey import Kernel


class TestKernelEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` call and check afterwards
      that the output is correct.
    """
    @patch(
        'archey.archey.check_output',
        return_value='X.Y.Z-R-arch\n'
    )
    def test(self, check_output_mock):
        self.assertEqual(Kernel().value, 'X.Y.Z-R-arch')


if __name__ == '__main__':
    unittest.main()
