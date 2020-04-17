"""Test module for Archey's distribution detection module"""

import unittest
from unittest.mock import patch

from archey.entries.distro import Distro


class TestDistroEntry(unittest.TestCase):
    """We mock the `distro` vendor module call, as long as the `check_output` one"""
    @patch(
        'archey.entries.distro.distro.name',  # `distro.name` output
        return_value="""\
NAME VERSION (CODENAME)\
""")
    @patch(
        'archey.entries.distro.check_output',  # `uname` output
        return_value="""\
ARCHITECTURE
""")
    def test(self, _, __):
        """Test for `distro` and `uname` outputs concatenation"""
        self.assertEqual(
            Distro().value,
            'NAME VERSION (CODENAME) [ARCHITECTURE]'
        )


if __name__ == '__main__':
    unittest.main()
