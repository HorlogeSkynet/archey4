"""`archey.test.entries` module initialization file"""

from copy import deepcopy
from functools import wraps

import unittest
from unittest.mock import MagicMock, patch

from archey.configuration import Configuration
from archey.constants import DEFAULT_CONFIG
from archey.entry import Entry


class HelperMethods:
    """
    This class contains helper methods we commonly use in our entry unit tests.
    We kindly borrow `update_recursive` class method from `Configuration` to DRY its implementation.
    """
    @staticmethod
    def entry_mock(entry, configuration=None):
        """
        Creates a placeholder "instance" of the entry class passed, with a clean default
        `_configuration` which is optionally updated by `configuration`.

        It can be used to very cleanly unit-test instance methods of a class,
        by passing it in (after setting appropriate attributes).

        The attributes defined are not instance attributes, however since this isn't
        technically an instance, they are used in place of the respective instance attributes.
        """
        # We spec to the entry so non-existent methods can't be called...
        # ...and wrap it, to inherit its methods.
        instance_mock = MagicMock(spec=entry, wraps=entry)
        # These instance-attributes are quite important, so let's mimic them.
        instance_mock.name = str(entry.__name__)
        instance_mock.value = None  # (entry default)

        # Let's initially give the entry configuration the defaults.
        # We deep-copy `DEFAULT_CONFIG` to prevent its mutation.
        entry_configuration = deepcopy(DEFAULT_CONFIG)
        # Then, let's merge in `configuration` recursively.
        Configuration.update_recursive(entry_configuration, (configuration or {}))
        # Finally, replaces the internal (and private!) `_configuration` attribute by...
        # ... the corresponding configuration object.
        setattr(instance_mock, '_configuration', entry_configuration)

        return instance_mock

    @staticmethod
    def patch_clean_configuration(method_definition=None, *, configuration=None):
        """
        Decorator for an entry test definition, which sets the entry's `_configuration` attribute to
        the Archey defaults, optionally updated with `configuration`.
        """
        # Let's initially give the entry configuration the defaults.
        # We deep-copy `DEFAULT_CONFIG` to prevent its mutation.
        entry_configuration = deepcopy(DEFAULT_CONFIG)
        # Then, let's merge in `configuration` recursively.
        Configuration.update_recursive(entry_configuration, (configuration or {}))

        def decorator_patch_clean_configuration(method):
            @wraps(method)
            def wrapper_patch_clean_configuration(*args, **kwargs):
                with patch('archey.entry.Configuration', autospec=True) as config_instance_mock:
                    # Mock "publicly" used methods.
                    config_instance_mock().get = entry_configuration.get
                    config_instance_mock().__iter__ = lambda _: iter(entry_configuration.items())
                    return method(*args, **kwargs)

            return wrapper_patch_clean_configuration

        if method_definition is None:
            return decorator_patch_clean_configuration

        return decorator_patch_clean_configuration(method_definition)


class TestHelperMethods(unittest.TestCase, HelperMethods):
    """This class implements test cases for our helper methods."""
    class _SimpleEntry(Entry):
        """A simple (sub-)class inheriting from `Entry` to use in testing."""
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

    def test_entry_mock_defaults(self):
        """Test `entry_mock`s default attributes."""
        simple_mock_instance = self.entry_mock(TestHelperMethods._SimpleEntry)
        self.assertEqual(simple_mock_instance.name, '_SimpleEntry')
        self.assertIsNone(simple_mock_instance.value)
        self.assertDictEqual(simple_mock_instance._configuration, DEFAULT_CONFIG)  # pylint: disable=protected-access

    def test_entry_mock_spec(self):
        """Test `entry_mock`s speccing."""
        simple_mock_instance = self.entry_mock(TestHelperMethods._SimpleEntry)
        with self.assertRaises(AttributeError):
            # We shouldn't be able to call methods that don't exist...
            simple_mock_instance.not_a_method()
            # ...or get attributes that don't exist.
            _ = simple_mock_instance.not_an_attribute
        # However we _should_ be able to set an attribute then use it.
        simple_mock_instance.is_simple = True
        self.assertTrue(simple_mock_instance.is_simple)

    def test_entry_mock_wrap(self):
        """Test `entry_mock`s class wrapping."""
        simple_mock_instance = self.entry_mock(TestHelperMethods._SimpleEntry)
        self.assertEqual(simple_mock_instance.meaning_of_life(), 42)
        simple_mock_instance.name = 'A simple entry!'
        self.assertEqual(simple_mock_instance.my_name(simple_mock_instance), 'A simple entry!')

    @patch.dict(
        DEFAULT_CONFIG,
        values={
            'a_key': 'a_value',
            'a_dict': {
                'key_1': 1,
                'key_2': 2
            }
        },
        clear=True
    )
    def test_entry_mock_configuration_setting(self):
        """Test `entry_mock`s configuration setting."""
        configuration_dict = {
            'another_key': 'another_value',  # Adding a key-value pair.
            'a_dict': {
                'key_1': 10  # Updating a nested key-value pair.
            }
        }
        simple_mock_instance = self.entry_mock(TestHelperMethods._SimpleEntry, configuration_dict)
        self.assertDictEqual(
            simple_mock_instance._configuration,  # pylint: disable=protected-access
            {
                'a_key': 'a_value',
                'another_key': 'another_value',
                'a_dict': {
                    'key_1': 10,
                    'key_2': 2
                }
            }
        )

    def test_patch_clean_configuration_defaults(self):
        """Test the default configuration-setting of `patch_clean_configuration."""
        @HelperMethods.patch_clean_configuration
        def test(self):
            simple_entry = TestHelperMethods._SimpleEntry()
            self.assertDictEqual(
                dict(simple_entry._configuration),  # pylint: disable=protected-access
                DEFAULT_CONFIG
            )

        test(self)

    @patch.dict(
        DEFAULT_CONFIG,
        values={
            'a_key': 'a_value',
            'a_dict': {
                'key_1': 1,
                'key_2': 2
            }
        },
        clear=True
    )
    def test_patch_clean_configuration_setting(self):
        """Test `patch_clean_configuration`s configuration setting."""
        configuration_dict = {
            'another_key': 'another_value',  # Adding a key-value pair.
            'a_dict': {
                'key_1': 10  # Updating a nested key-value pair.
            }
        }
        @HelperMethods.patch_clean_configuration(
            configuration=configuration_dict
        )
        def test(self):
            simple_entry = TestHelperMethods._SimpleEntry()
            self.assertDictEqual(
                dict(simple_entry._configuration),  # pylint: disable=protected-access
                {
                    'a_key': 'a_value',
                    'another_key': 'another_value',
                    'a_dict': {
                        'key_1': 10,
                        'key_2': 2
                    }
                }
            )

        test(self)
