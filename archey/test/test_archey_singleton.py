"""Test module for `archey.singleton`"""

import unittest

from abc import ABCMeta

from archey.singleton import Singleton


class _SimpleCounter(metaclass=Singleton):
    def __init__(self):
        self._counter = 0
        self.an_object = {}

    def increment(self):
        """Adds `1` to the internal counter"""
        self._counter += 1

    def get(self):
        """Returns the internal counter value"""
        return self._counter


class TestSingletonUtil(unittest.TestCase):
    """Test cases for our `Singleton` meta-class"""
    def test_singleton_itself(self):
        """Verifies `Singleton` hierarchy"""
        self.assertTrue(issubclass(Singleton, type))
        self.assertTrue(issubclass(Singleton, ABCMeta))
        self.assertTrue(isinstance(_SimpleCounter, Singleton))

    def test_singleton_subclass_instances(self):
        """Simple tests for `Singleton` sub-class instantiation results"""
        counter_1 = _SimpleCounter()
        counter_2 = _SimpleCounter()
        self.assertIs(counter_1, counter_2)
        self.assertEqual(counter_1, counter_2)

        # Modifies `counter_1`'s internal value.
        counter_1.increment()
        # These values should be equals.
        self.assertEqual(counter_1.get(), counter_2.get())

        # Internal objects are also the same.
        self.assertIs(counter_1.an_object, counter_2.an_object)

    def test_singleton_instantiations(self):
        """Simple test for `Singleton` (direct) instantiation"""
        self.assertRaises(TypeError, Singleton)


if __name__ == '__main__':
    unittest.main()
