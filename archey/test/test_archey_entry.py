"""Test module for `archey.entry`"""

import unittest
from abc import ABC

from archey.entry import Entry


class _SimpleEntry(Entry):
    _PRETTY_NAME = "Simple Entry"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def output(self, output) -> None:
        """Reverse order!"""
        output.append((self.value, self.name))


class TestEntry(unittest.TestCase):
    """Simple test cases for our `Entry` abstract class"""

    def test_entry_itself(self):
        """Check `Entry`'s type and direct-instantiation failure"""
        self.assertTrue(issubclass(_SimpleEntry, ABC))
        self.assertTrue(issubclass(_SimpleEntry, Entry))
        self.assertRaises(TypeError, Entry)

    def test_entry_disabling(self):
        """Test `Entry` _disabling_"""
        simple_entry = _SimpleEntry()
        self.assertTrue(simple_entry)

        simple_entry = _SimpleEntry(options={"disabled": True})
        self.assertIsNone(simple_entry)

        simple_entry = _SimpleEntry(options={"disabled": False})
        self.assertNotIn("disabled", simple_entry.options)

    def test_entry_usage(self):
        """Test `Entry` instantiation and parameters passing"""
        # No name passed as parameter, let's use internal defined "pretty name".
        simple_entry = _SimpleEntry()
        self.assertEqual(simple_entry.name, "Simple Entry")
        self.assertIsNone(simple_entry.value)

        # No `_PRETTY_NAME` is defined : proper fall-back on entry internal name.
        delattr(_SimpleEntry, "_PRETTY_NAME")
        self.assertEqual(_SimpleEntry().name, "_SimpleEntry")

        # A name is passed as parameter, it has to be chosen.
        simple_entry = _SimpleEntry("T", "est")
        self.assertEqual(simple_entry.name, "T")
        self.assertEqual(simple_entry.value, "est")

    def test_entry_output_overriding(self):
        """Check `Entry.output` public method overriding"""
        simple_entry = _SimpleEntry("is this", "ordered")
        output = []
        simple_entry.output(output)
        self.assertListEqual(output, [("ordered", "is this")])
