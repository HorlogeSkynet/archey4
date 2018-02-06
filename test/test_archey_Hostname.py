
import unittest

from archey.archey import Hostname


class TestHostnameEntry(unittest.TestCase):
    def test(self):
        self.assertNotIn(Hostname().value, [None, ''])


if __name__ == '__main__':
    unittest.main()
