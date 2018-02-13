
import unittest
from unittest.mock import mock_open, patch

from archey.archey import Uptime


class TestUptimeEntry(unittest.TestCase):
    """
    Here, we mock the `open` call and imitate `/proc/uptime` content.
    """
    @patch(
        'archey.archey.open',
        mock_open(
            read_data='0.00 XXXX.XX\n'
        )
    )
    def test_warming_up(self):
        self.assertEqual(Uptime().value, '< 1 minute')

    @patch(
        'archey.archey.open',
        mock_open(
            read_data='120.25 XXXX.XX\n'
        )
    )
    def test_minutes_only(self):
        self.assertEqual(Uptime().value, '2 minutes')

    @patch(
        'archey.archey.open',
        mock_open(
            read_data='7260.50 XXXX.XX\n'
        )
    )
    def test_hours_and_minute(self):
        self.assertEqual(Uptime().value, '2 hours and 1 minute')

    @patch(
        'archey.archey.open',
        mock_open(
            read_data='90120.75 XXXX.XX\n'
        )
    )
    def test_day_and_hour_and_minutes(self):
        self.assertEqual(Uptime().value, '1 day, 1 hour and 2 minutes')

    @patch(
        'archey.archey.open',
        mock_open(
            read_data='259380.99 XXXX.XX\n'
        )
    )
    def test_days_and_minutes(self):
        self.assertEqual(Uptime().value, '3 days and 3 minutes')


if __name__ == '__main__':
    unittest.main()
