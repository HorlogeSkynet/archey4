"""Test module for Archey's uptime detection module"""

import unittest
from unittest.mock import mock_open, patch, MagicMock
from datetime import timedelta
from itertools import product

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
        uptime = Uptime()

        output_mock = MagicMock()
        uptime.output(output_mock)

        self.assertDictEqual(
            uptime.value,
            {
                'days': 0,
                'hours': 0,
                'minutes': 0,
                'seconds': 0
            }
        )
        self.assertEqual(
            output_mock.append.call_args[0][1],
            '< 1 minute'
        )

    @patch(
        'archey.entries.uptime.open',
        mock_open(
            read_data='120.25 XXXX.XX\n'
        ),
        create=True
    )
    def test_minutes_only(self):
        """Test when only minutes should be displayed"""
        output_mock = MagicMock()
        Uptime().output(output_mock)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            '2 minutes'
        )

    @patch(
        'archey.entries.uptime.open',
        mock_open(
            read_data='7260.50 XXXX.XX\n'
        ),
        create=True
    )
    def test_hours_and_minute(self):
        """Test when only hours AND minutes should be displayed"""
        output_mock = MagicMock()
        Uptime().output(output_mock)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            '2 hours and 1 minute'
        )

    @patch(
        'archey.entries.uptime.open',
        mock_open(
            read_data='90120.75 XXXX.XX\n'
        ),
        create=True
    )
    def test_day_and_hour_and_minutes(self):
        """Test when only days, hours AND minutes should be displayed"""
        output_mock = MagicMock()
        Uptime().output(output_mock)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            '1 day, 1 hour and 2 minutes'
        )

    @patch(
        'archey.entries.uptime.open',
        mock_open(
            read_data='259381.99 XXXX.XX\n'
        ),
        create=True
    )
    def test_days_and_minutes(self):
        """Test when only days AND minutes should be displayed"""
        uptime = Uptime()

        output_mock = MagicMock()
        uptime.output(output_mock)

        self.assertDictEqual(
            uptime.value,
            {
                'days': 3,
                'hours': 0,
                'minutes': 3,
                'seconds': 1
            }
        )
        self.assertEqual(
            output_mock.append.call_args[0][1],
            '3 days and 3 minutes'
        )

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
        We only test one clock as all clocks rely on the same built-in `time.clock_gettime` method.
        """
        output_mock = MagicMock()
        Uptime().output(output_mock)
        self.assertEqual(
            output_mock.append.call_args[0][1],
            '16 minutes'
        )

    @patch('archey.entries.uptime.check_output')
    def test_uptime_fallback(self, check_output_mock):
        """Test `uptime` command parsing"""
        # Create an uptime instance to perform testing.
        # It doesn't matter that its `__init__` will be called.
        uptime_inst = Uptime()

        # Keys: `uptime` outputs; values: expected `timedelta` instances.
        # We will test these with various time formats (and various numbers of users).
        # pylint: disable=line-too-long
        test_uptime_cases = {
            # Recently booted:
            '{time} up 0 sec, {user_loadavg}': timedelta(seconds=0),  # BSD, just booted
            '{time} up 1 sec, {user_loadavg}': timedelta(seconds=1),  # BSD, < 1 min uptime
            '{time} up 12 secs, {user_loadavg}': timedelta(seconds=12),  # BSD, < 1 min uptime
            '{time} up 0 min, {user_loadavg}': timedelta(minutes=0),  # Linux, < 1 min uptime
            '{time} up 1 min, {user_loadavg}': timedelta(minutes=1),
            # 1 min to 1 day
            '{time} up 12 mins, {user_loadavg}': timedelta(minutes=12),
            '{time} up 12 min, {user_loadavg}': timedelta(minutes=12),  # Variation without plural minutes
            '{time} up 1:00, {user_loadavg}': timedelta(hours=1),
            '{time} up 1:01, {user_loadavg}': timedelta(hours=1, minutes=1),
            '{time} up 1:23, {user_loadavg}': timedelta(hours=1, minutes=23),
            '{time} up 12:34, {user_loadavg}': timedelta(hours=12, minutes=34),
            # 1 day to 2 days
            '{time} up 1 day, 0 sec, {user_loadavg}': timedelta(days=1),  # BSD
            '{time} up 1 day, 1 sec, {user_loadavg}': timedelta(days=1, seconds=1),  # BSD
            '{time} up 1 day, 12 secs, {user_loadavg}': timedelta(days=1, seconds=12),  # BSD
            '{time} up 1 day, 0 min, {user_loadavg}': timedelta(days=1),  # Linux
            '{time} up 1 day, 1 min, {user_loadavg}': timedelta(days=1, minutes=1),
            '{time} up 1 day, 12 mins, {user_loadavg}': timedelta(days=1, minutes=12),
            '{time} up 1 day, 12 min, {user_loadavg}': timedelta(days=1, minutes=12),  # Variation without plural minutes
            '{time} up 1 day, 1:00, {user_loadavg}': timedelta(days=1, hours=1),
            '{time} up 1 day, 1:01, {user_loadavg}': timedelta(days=1, hours=1, minutes=1),
            '{time} up 1 day, 1:23, {user_loadavg}': timedelta(days=1, hours=1, minutes=23),
            '{time} up 1 day, 12:34, {user_loadavg}': timedelta(days=1, hours=12, minutes=34),
            # 2 days onwards
            '{time} up 12 days, 0 sec, {user_loadavg}': timedelta(days=12),  # BSD
            '{time} up 12 days, 1 sec, {user_loadavg}': timedelta(days=12, seconds=1),  # BSD
            '{time} up 12 days, 12 secs, {user_loadavg}': timedelta(days=12, seconds=12),  # BSD
            '{time} up 12 days, 0 min, {user_loadavg}': timedelta(days=12),  # Linux
            '{time} up 12 days, 1 min, {user_loadavg}': timedelta(days=12, minutes=1),
            '{time} up 12 days, 12 mins, {user_loadavg}': timedelta(days=12, minutes=12),
            '{time} up 12 day, 12 min, {user_loadavg}': timedelta(days=12, minutes=12),  # Variation without plural minutes
            '{time} up 12 days, 1:00, {user_loadavg}': timedelta(days=12, hours=1),
            '{time} up 12 days, 1:01, {user_loadavg}': timedelta(days=12, hours=1, minutes=1),
            '{time} up 12 days, 1:23, {user_loadavg}': timedelta(days=12, hours=1, minutes=23),
            '{time} up 12 days, 12:34, {user_loadavg}': timedelta(days=12, hours=12, minutes=34),
            # Very long uptimes - sanity check :)
            '{time} up 500 days, 0 sec, {user_loadavg}': timedelta(days=500),  # BSD
            '{time} up 500 days, 1 sec, {user_loadavg}': timedelta(days=500, seconds=1),  # BSD
            '{time} up 500 days, 12 secs, {user_loadavg}': timedelta(days=500, seconds=12),  # BSD
            '{time} up 500 days, 0 min, {user_loadavg}': timedelta(days=500),  # Linux
            '{time} up 500 days, 1 min, {user_loadavg}': timedelta(days=500, minutes=1),
            '{time} up 500 days, 12 mins, {user_loadavg}': timedelta(days=500, minutes=12),
            '{time} up 500 day, 12 min, {user_loadavg}': timedelta(days=500, minutes=12),  # Variation without plural minutes
            '{time} up 500 days, 1:00, {user_loadavg}': timedelta(days=500, hours=1),
            '{time} up 500 days, 1:01, {user_loadavg}': timedelta(days=500, hours=1, minutes=1),
            '{time} up 500 days, 1:23, {user_loadavg}': timedelta(days=500, hours=1, minutes=23),
            '{time} up 500 days, 12:34, {user_loadavg}': timedelta(days=500, hours=12, minutes=34),
        }
        # pylint: enable=line-too-long

        # Variations of the time in the `{time}` section.
        # These _should_ be avoided when we set the locale in `check_output`,
        # however let's check we can handle them anyway, just in case.
        time_variations = (
            '0:00', '9:43 ', '11:37  ', '19:21', '23:59',
            '12:00am', '1:10am', '1:10pm ', '6:43pm ', '8:26am ',
            '03:14:15', '09:26:12 ', '23:19:20  ',
            'nonsense_time  ', 'hopefully_works_anyway ',
            '  even with strange spacing!'
        )

        # Variations of the user count and load average section.
        # For this, we'll just combine user variations with a few load average variations.
        user_variations = (
            '1 user ', '1 user  ', ' 1 user, ', ' 1 user,  ',
            '2 users ', '2 users  ', '  2 users, ', '  2 users,  ',
            '15 users ', '15 users  ', ' 15 users, ', ' 15 users,  ',
            '150 users ', '150 users  ', '150 users, ', '150 users,  ',
        )
        loadavg_variations = (
            'load averages: 1.95 1.28 2.10',
            'load average: 0.13, 0.17, 0.13',
            'we never match this part so the content here',
            '  should not affect our parsing'
        )
        user_loadavg_variations = [
            user + loadavg
            for user in user_variations
            for loadavg in loadavg_variations
        ]

        for uptime_output, expected_delta in test_uptime_cases.items():
            # We use `itertools.product` to get the permutations of our variations
            # since there are a lot of them! (a list comprehension would be slower)
            for variations in product(time_variations, user_loadavg_variations):
                check_output_mock.return_value = uptime_output.format(
                    time=variations[0],
                    user_loadavg=variations[1]
                )
                self.assertEqual(
                    uptime_inst._parse_uptime_cmd(),  # pylint: disable=protected-access
                    expected_delta,
                    msg='`uptime` output: "{0}"'.format(
                        uptime_output.format(
                            time=variations[0],
                            user_loadavg=variations[1]
                        )
                    )
                )

    @patch(
        'archey.entries.uptime.open',
        side_effect=PermissionError(),
        create=True
    )
    @patch(
        'archey.entries.uptime.check_output',
        side_effect=FileNotFoundError()
    )
    @patch.object(
        Uptime,
        '_clock_uptime',
        side_effect=RuntimeError()
    )
    def test_procps_missing(self, _, __, ___):
        """Test `uptime` failure (program exit) when no uptime sources are available"""
        self.assertRaises(SystemExit, Uptime)


if __name__ == '__main__':
    unittest.main()
