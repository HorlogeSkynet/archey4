
import unittest

from archey.archey import User


class TestUserEntry(unittest.TestCase):
    def test(self):
        self.assertNotIn(User().value, [None, ''])


if __name__ == '__main__':
    unittest.main()
