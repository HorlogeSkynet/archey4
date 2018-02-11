
import unittest
from unittest.mock import patch

from archey.archey import Distro


class TestDistroEntry(unittest.TestCase):
    """
    Here, we mock the `check_output` calls and check afterwards
      that the outputs are correct.
    """
    @patch(
        'archey.archey.check_output',
        side_effect=[
            b'Distro OS X.Y (name)\n',  # `lsb_release` output
            b'ARCH\n'                   # `uname` output
        ]
    )
    def test(self, check_output_mock):
        self.assertEqual(
            Distro().value,
            'Distro OS X.Y (name) ARCH'
        )


if __name__ == '__main__':
    unittest.main()
