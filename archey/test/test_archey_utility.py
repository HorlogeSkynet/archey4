"""Test module for `archey.configuration`"""

import unittest

from archey.utility import Utility


class TestUtility(unittest.TestCase):
    """
    Simple test cases to check the behavior of `Utility` singleton utility class.
    Values will be manually set in the tests below.
    """

    def test_update_recursive(self):
        """Test for the `update_recursive` class method"""
        test_dict = {
            "allow_overriding": True,
            "suppress_warnings": False,
            "default_strings": {
                "no_address": "No Address",
                "not_detected": "Not detected",
            },
            "colors_palette": {
                "use_unicode": False,
            },
            "ip_settings": {
                "lan_ip_max_count": 2,
            },
            "temperature": {
                "use_fahrenheit": False,
            },
        }

        # We change existing values, add new ones, and omit some others.
        Utility.update_recursive(
            test_dict,
            {
                "suppress_warnings": True,
                "colors_palette": {
                    "use_unicode": False,
                },
                "default_strings": {
                    "no_address": "\xde\xad \xbe\xef",
                    "not_detected": "Not detected",
                    "virtual_environment": "Virtual Environment",
                },
                "temperature": {
                    "a_weird_new_dict": [
                        None,
                        "l33t",
                        {
                            "really": "one_more_?",
                        },
                    ],
                },
            },
        )

        self.assertDictEqual(
            test_dict,
            {
                "allow_overriding": True,
                "suppress_warnings": True,
                "colors_palette": {
                    "use_unicode": False,
                },
                "default_strings": {
                    "no_address": "\xde\xad \xbe\xef",
                    "not_detected": "Not detected",
                    "virtual_environment": "Virtual Environment",
                },
                "ip_settings": {
                    "lan_ip_max_count": 2,
                },
                "temperature": {
                    "use_fahrenheit": False,
                    "a_weird_new_dict": [
                        None,
                        "l33t",
                        {
                            "really": "one_more_?",
                        },
                    ],
                },
            },
        )

    def test_version_to_semver_segments(self):
        """Check `version_to_semver_segments` implementation"""
        self.assertTupleEqual(Utility.version_to_semver_segments("1.2.3"), (1, 2, 3))
        self.assertTupleEqual(Utility.version_to_semver_segments("1.2.3.4-beta5"), (1, 2, 3, 4))
        self.assertTupleEqual(Utility.version_to_semver_segments("1"), (1,))
