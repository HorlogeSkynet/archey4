"""Test module for Archey's uptime detection module"""

import unittest
from unittest.mock import mock_open, patch
from datetime import timedelta

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
        """Test when only days AND minutes should be displayed"""
        self.assertEqual(Uptime().value, '3 days and 3 minutes')

    @patch(
        'archey.entries.uptime.open',
        side_effect=PermissionError(),
        create=True
    )
    @patch(
        'archey.entries.uptime.time.CLOCK_BOOTTIME',  # Ensure first `getattr` call succeeds anyhow.
        create=True
    )
    @patch(
        'archey.entries.uptime.time.clock_gettime',
        return_value=1000,
        create=True
    )
    def test_clock_fallback(self, _, __, ___):
        """
        Test when we can't access /proc/uptime on Linux/macOS/BSD.
        We only test one clock as all clocks rely on the same builtin `time.clock_gettime` method.
        """
        self.assertEqual(Uptime().value, '16 minutes')

    @patch('archey.entries.uptime.check_output')
    def test_uptime_fallback(self, check_output_mock):
        """Test `uptime` command parsing"""
        # Create an uptime instance to perform testing.
        # It doesn't matter that its `__init__` will be called.
        uptime_inst = Uptime()

        # Keys: `uptime` outputs; values: expected `timedelta` instances.
        # These outputs have been gathered from various *NIX sytems (with various locales).
        # pylint: disable=line-too-long
        test_cases = {
            '19:52  up 14 mins, 2 users, load averages: 2.95 4.19 4.31': timedelta(minutes=14),
            '8:03 up 52 days, 20:47, 3 users, load averages: 1.36 1.42 1.40': timedelta(days=52, hours=20, minutes=47),
            '22:19 up 54 days, 1 min, 4 users, load averages: 2.08 2.06 2.27': timedelta(days=54, minutes=1),
            '11:53  up  3:02, 2 users, load averages: 0,32 0,34 0,43': timedelta(hours=3, minutes=2),
            '12:55pm  up 105 days, 21 hrs,  2 users,  load average: 0.26, 0.26, 0.26': timedelta(days=105, hours=21),
            '1:41pm  up 105 days, 21:46,  2 users,  load average: 0.28, 0.28, 0.27': timedelta(days=105, hours=21, minutes=46),
            '8:27  up 1 day, 17:06, 1 user, load averages: 1,01 0,87 0,79': timedelta(days=1, hours=17, minutes=6),
            '06:27:33 up 4 days,  2:36,  2 users,  load average: 0.16, 0.26, 0.27': timedelta(days=4, hours=2, minutes=36),
            '06:28:26 up 54 min,  127 users,  load average: 6.34, 6.28, 6.27': timedelta(minutes=54),
            '17:35pm  up 5 days  9:24,  9 users,  load average: 0.30, 0.28, 0.28': timedelta(days=5, hours=9, minutes=24),
            '17:36:15 up  8:44,  2 users,  load average: 0.09, 0.30, 0.41': timedelta(hours=8, minutes=44),
            '03:14:20 up 1 min,  2 users,  load average: 2.28, 1.29, 0.50': timedelta(minutes=1),
            '04:12:29 up 59 min,  5 users,  load average: 0.06, 0.08, 0.48': timedelta(minutes=59),
            '05:14:09 up  2:01,  5 users,  load average: 0.13, 0.10, 0.45': timedelta(hours=2, minutes=1),
            '03:13:19 up 1 day, 0 min,  8 users,  load average: 0.01, 0.04, 0.05': timedelta(days=1),
            '04:13:19 up 1 day,  1:00,  8 users,  load average: 0.02, 0.05, 0.21': timedelta(days=1, hours=1),
            '12:49:10 up 25 days, 21:30, 28 users,  load average: 0.50, 0.66, 0.52': timedelta(days=25, hours=21, minutes=30)
        }
        # pylint: enable=line-too-long

        for uptime_output, expected_delta in test_cases.items():
            check_output_mock.return_value = uptime_output
            self.assertEqual(
                uptime_inst._parse_uptime_cmd(), # pylint: disable=protected-access
                expected_delta,
                msg='`uptime` output: {}'.format(uptime_output)
            )

    @patch(
        'archey.entries.uptime.open',
        side_effect=PermissionError(),
        create=True
    )
    @patch(
        'archey.entries.uptime.check_output',
        side_effect=FileNotFoundError(),
        create=True
    )
    @patch.object(
        Uptime,
        '_clock_uptime',
        side_effect=RuntimeError()
    )
    def test_procps_missing(self, _, __, ___):
        """Test `uptime` failure when no uptime sources are available"""
        with self.assertRaises(SystemExit):
            Uptime()


if __name__ == '__main__':
    unittest.main()
