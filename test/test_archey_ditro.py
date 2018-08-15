
import unittest
from unittest.mock import patch

from archey.archey import Distro


class TestDistroEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` calls and check afterwards
      that the outputs are correct.
    """
    @patch(
        'archey.archey.distro.name',  # `distro.name` output
        return_value="""\
NAME VERSION (CODENAME)\
""")
    @patch(
        'archey.archey.check_output',  # `uname` output
        return_value="""\
ARCHITECTURE
""")
    def test(self, check_output_mock, distro_name_mock):
        self.assertEqual(
            Distro().value,
            'NAME VERSION (CODENAME) [ARCHITECTURE]'
        )


if __name__ == '__main__':
    unittest.main()
