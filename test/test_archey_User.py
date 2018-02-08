
import unittest

from archey.archey import User


class TestUserEntry(unittest.TestCase):
    """
    For this entry, we'll just verify that the output is non-null.
    """
    def test(self):
        self.assertNotIn(User().value, [None, ''])


if __name__ == '__main__':
    unittest.main()
