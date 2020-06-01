"""`archey.test` module initialization file"""

import unittest
from unittest.mock import MagicMock

from archey.constants import DEFAULT_CONFIG
from archey.entry import Entry


# This global stops `unittest` from printing tracebacks _beyond_ our custom assertion.
# See <https://stackoverflow.com/a/49929579>.
__unittest = True  # pylint: disable=invalid-name


# From <https://stackoverflow.com/a/15868615>.
class CustomAssertions:
    """This class defines our custom assertion methods being used in Archey unit testing"""
    @staticmethod
    def assertListEmpty(obj):  # pylint: disable=invalid-name
        """Simple method to check that passed `obj` is an **empty** `list`"""
        if not isinstance(obj, list):
            raise AssertionError('First sequence is not a list: ' + str(obj))

        if obj:
            raise AssertionError('First sequence is not empty: ' + str(obj))


class HelperMethods:
    """This class contains helper methods we commonly use in our unit tests."""
    @staticmethod
    def entry_mock(entry):
        """
        Create a mock instance of the entry class passed.
        Crucially, this method doesn't run `__init__`, so instance attributes are never present.
        """
        # We spec to the entry so non-existent methods can't be called...
        # ...and wrap it, to inherit its methods.
        instance_mock = MagicMock(spec=entry, wraps=entry)
        # Methods (ideally) only ever use the below attributes.
        instance_mock.name = str(entry.__name__)
        instance_mock.value = None  # (entry default)
        # Let's set the default configuration as defined in `archey.constants`.
        instance_mock._configuration = DEFAULT_CONFIG  # pylint: disable=protected-access

        return instance_mock


class TestCustomAssertions(unittest.TestCase, CustomAssertions):
    """This class implements test cases for the custom Archey unit testing framework (#inception)"""
    def test_assert_list_empty(self):
        """Test cases for our `self.assertListEmpty` custom assertion"""
        self.assertListEmpty([])
        self.assertRaises(AssertionError, self.assertListEmpty, {})
        self.assertRaises(AssertionError, self.assertListEmpty, 'test')
        self.assertRaises(AssertionError, self.assertListEmpty, ['test'])


class _SimpleEntry(Entry):
    """A simple class ineheriting from `Entry` to use in testing."""
    def __init__(self):
        super().__init__()
        self.name = 'meaning_of_life'
        self.value = self.meaning_of_life()

    def my_name(self):
        """Returns the entry name."""
        return self.name

    @staticmethod
    def meaning_of_life():
        """Widely debated..."""
        return 42


class TestHelperMethods(unittest.TestCase, HelperMethods):
    """This class implements test cases for our helper methods."""
    def test_entry_mock_defaults(self):
        """Test `self.entry_mock`s default attributes."""
        simple_mock_instance = self.entry_mock(_SimpleEntry)
        self.assertEqual(simple_mock_instance.name, '_SimpleEntry')
        self.assertIsNone(simple_mock_instance.value)
        self.assertDictEqual(simple_mock_instance._configuration, DEFAULT_CONFIG)  # pylint: disable=protected-access

    def test_entry_mock_spec(self):
        """Test `self.entry_mock`s speccing."""
        simple_mock_instance = self.entry_mock(_SimpleEntry)
        with self.assertRaises(AttributeError):
            # We shouldn't be able to call methods that don't exist...
            simple_mock_instance.not_a_method()
            # ...or get attributes that don't exist.
            _ = simple_mock_instance.not_an_attribute
        # However we _should_ be able to set an attribute then use it.
        simple_mock_instance.is_simple = True
        self.assertTrue(simple_mock_instance.is_simple)

    def test_entry_mock_wrap(self):
        """Test `self.entry_mock`s class wrapping."""
        simple_mock_instance = self.entry_mock(_SimpleEntry)
        self.assertEqual(simple_mock_instance.meaning_of_life(), 42)
        simple_mock_instance.name = 'A simple entry!'
        self.assertEqual(simple_mock_instance.my_name(simple_mock_instance), 'A simple entry!')
