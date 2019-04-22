"""Test module for Archey's uptime detection module"""

import unittest
from unittest.mock import mock_open, patch

from archey.entries.uptime import Uptime


class TestUptimeEntry(unittest.TestCase):
    """
    Here, we mock the `open` call and imitate `/proc/uptime` content.
    """
    @patch(
        'archey.entries.uptime.open',
        mock_open(
            read_data='0.00 XXXX.XX\n'
        ),
        create=True
    )
    def test_warming_up(self):
        """Test when the device has just been started..."""
        self.assertEqual(Uptime().value, '< 1 minute')

    @patch(
        'archey.entries.uptime.open',
        mock_open(
            read_data='120.25 XXXX.XX\n'
        ),
        create=True
    )
    def test_minutes_only(self):
        """Test when only minutes should be displayed"""
        self.assertEqual(Uptime().value, '2 minutes')

    @patch(
        'archey.entries.uptime.open',
        mock_open(
            read_data='7260.50 XXXX.XX\n'
        ),
        create=True
    )
    def test_hours_and_minute(self):
        """Test when only hours AND minutes should be displayed"""
        self.assertEqual(Uptime().value, '2 hours and 1 minute')

    @patch(
        'archey.entries.uptime.open',
        mock_open(
            read_data='90120.75 XXXX.XX\n'
        ),
        create=True
    )
    def test_day_and_hour_and_minutes(self):
        """Test when only days, hours AND minutes should be displayed"""
        self.assertEqual(Uptime().value, '1 day, 1 hour and 2 minutes')

    @patch(
        'archey.entries.uptime.open',
        mock_open(
            read_data='259380.99 XXXX.XX\n'
        ),
        create=True
    )
    def test_days_and_minutes(self):
        """Test when only days ABD minutes should be displayed"""
        self.assertEqual(Uptime().value, '3 days and 3 minutes')


if __name__ == '__main__':
    unittest.main()
