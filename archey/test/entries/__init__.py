"""`archey.test.entries` module initialization file"""

import logging
import typing
import unittest
from copy import deepcopy
from functools import wraps
from unittest.mock import MagicMock, patch

from archey.configuration import DEFAULT_CONFIG, Configuration
from archey.entry import Entry
from archey.utility import Utility


class HelperMethods:
    """
    This class contains helper methods we commonly use in our entry unit tests.
    """

    @staticmethod
    def entry_mock(
        entry, options: typing.Optional[dict] = None, configuration: typing.Optional[dict] = None
    ) -> MagicMock:
        """
        Creates a placeholder "instance" of the entry class passed, with a clean default
        `_default_strings` which is optionally updated by `configuration`.

        It can be used to very cleanly unit-test instance methods of a class,
        by passing it in (after setting appropriate attributes).

        The attributes defined are not instance attributes, however since this isn't
        technically an instance, they are used in place of the respective instance attributes.
        """
        # We spec to the entry so non-existent methods can't be called...
        # ...and wrap it, to inherit its methods.
        instance_mock = MagicMock(spec=entry, wraps=entry)
        # These instance-attributes are quite important, so let's mimic them.
        instance_mock.name = getattr(entry, "_PRETTY_NAME") or str(entry.__name__)
        instance_mock.value = None  # (entry default)
        # We don't have default entry options defined outside of entries.
        instance_mock.options = options or {}

        # Let's initially give the entry configuration the defaults.
        # We deep-copy `DEFAULT_CONFIG` to prevent its mutation.
        default_configuration = deepcopy(DEFAULT_CONFIG)
        # Then, let's merge in `configuration` recursively.
        Utility.update_recursive(default_configuration, (configuration or {}))
        # Replaces the internal (and protected!) `_default_strings` attribute by...
        # ... the corresponding object from configuration.
        setattr(instance_mock, "_default_strings", default_configuration.get("default_strings"))
        # Finally provisions a proper `logging.Logger` instance for our mock.
        setattr(instance_mock, "_logger", logging.getLogger(entry.__module__))

        return instance_mock

    @staticmethod
    def patch_clean_configuration(
        method_definition: typing.Optional[typing.Callable] = None,
        *,
        configuration: typing.Optional[dict] = None,
    ) -> typing.Callable:
        """
        Decorator for an entry test definition, which sets the entry's `_default_strings` attribute
        to the Archey defaults, optionally updated with `configuration`.
        """
        # Let's initially give defaults to configuration objects.
        # We deep-copy `DEFAULT_CONFIG` to prevent its mutation.
        default_config = deepcopy(DEFAULT_CONFIG)
        # Then we recursively merge in passed `configuration`.
        Utility.update_recursive(default_config, (configuration or {}))

        def decorator_patch_clean_configuration(method: typing.Callable) -> typing.Callable:
            @wraps(method)
            def wrapper_patch_clean_configuration(*args, **kwargs):
                # `Configuration` singleton is used in `Entry` and `Output` unit-tested modules.
                with patch(
                    "archey.entry.Configuration", autospec=True
                ) as entry_config_instance_mock, patch(
                    "archey.output.Configuration", autospec=True
                ) as output_config_instance_mock:
                    # Mock "publicly" used methods.
                    entry_config_instance_mock().get = default_config.get
                    entry_config_instance_mock().__iter__ = iter(default_config.items())

                    output_config_instance_mock().get = default_config.get
                    output_config_instance_mock().__iter__ = iter(default_config.items())

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
            self.name = "meaning_of_life"
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
        self.assertEqual(simple_mock_instance.name, "_SimpleEntry")
        self.assertIsNone(simple_mock_instance.value)
        self.assertDictEqual(
            simple_mock_instance._default_strings,  # pylint: disable=protected-access
            DEFAULT_CONFIG.get("default_strings"),  # type: ignore
        )

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
        simple_mock_instance.name = "A simple entry!"
        self.assertEqual(simple_mock_instance.my_name(simple_mock_instance), "A simple entry!")

    @patch.dict(
        DEFAULT_CONFIG,
        values={
            "a_key": "a_value",
            "a_dict": {"key_1": 1, "key_2": 2},
            "default_strings": {},
        },
        clear=True,
    )
    def test_entry_mock_configuration_setting(self):
        """Test `entry_mock`s configuration setting."""
        configuration_dict = {
            "another_key": "another_value",  # Adding a key-value pair.
            "a_dict": {"key_1": 10},  # Updating a nested key-value pair.
        }
        simple_mock_instance = self.entry_mock(
            TestHelperMethods._SimpleEntry, configuration=configuration_dict
        )
        self.assertDictEqual(
            simple_mock_instance._default_strings,  # pylint: disable=protected-access
            DEFAULT_CONFIG.get("default_strings"),  # type: ignore
        )

    def test_patch_clean_configuration_defaults(self):
        """Test the default configuration-setting of `patch_clean_configuration."""

        @HelperMethods.patch_clean_configuration
        def test(self):
            simple_entry = TestHelperMethods._SimpleEntry()
            self.assertDictEqual(
                simple_entry._default_strings,  # pylint: disable=protected-access
                DEFAULT_CONFIG.get("default_strings"),
            )

        test(self)

    @patch.dict(
        DEFAULT_CONFIG,
        values={
            "a_key": "a_value",
            "a_dict": {"key_1": 1, "key_2": 2},
            "default_strings": {},
        },
        clear=True,
    )
    def test_patch_clean_configuration_setting(self):
        """Test `patch_clean_configuration`s configuration setting."""
        configuration_dict = {
            "another_key": "another_value",  # Adding a key-value pair.
            "a_dict": {"key_1": 10},  # Updating a nested key-value pair.
        }

        @HelperMethods.patch_clean_configuration(configuration=configuration_dict)
        def test(self):
            simple_entry = TestHelperMethods._SimpleEntry()
            self.assertDictEqual(
                simple_entry._default_strings,  # pylint: disable=protected-access
                DEFAULT_CONFIG.get("default_strings"),
            )

        test(self)
