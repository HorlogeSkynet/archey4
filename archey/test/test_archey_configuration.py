"""Test module for `archey.configuration`"""

import logging
import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from archey.configuration import Configuration


# To avoid edge-case issues due to singleton, we automatically reset internal `_instances`.
# This is done at the class-level.
@patch.dict(
    "archey.singleton.Singleton._instances",
    clear=True,
)
class TestConfiguration(unittest.TestCase):
    """
    Simple test cases to check the behavior of `Configuration` singleton utility class.
    Values will be manually set in the tests below.
    """

    @patch(
        # `_load_configuration` method is mocked to "ignore" local system configurations.
        "archey.configuration.Configuration._load_configuration",
        Mock(),
    )
    def test_get(self):
        """Test the `get` binding method to configuration elements"""
        configuration = Configuration()
        with patch.dict(
            configuration._config,  # pylint: disable=protected-access
            {
                "ip_settings": {
                    "lan_ip_max_count": 2,
                },
                "temperature": {
                    "use_fahrenheit": False,
                },
            },
        ):
            self.assertEqual(configuration.get("ip_settings")["lan_ip_max_count"], 2)
            self.assertFalse(configuration.get("temperature")["use_fahrenheit"])
            self.assertTrue(configuration.get("does_not_exist", True))
            self.assertIsNone(configuration.get("does_not_exist_either"))

    def test_load_configuration(self):
        """Test for configuration loading from file, and overriding flag"""
        configuration = Configuration()
        with patch.dict(
            configuration._config,  # pylint: disable=protected-access
            {
                "allow_overriding": True,
                "suppress_warnings": False,
                "colors_palette": {
                    "use_unicode": False,
                },
                "ip_settings": {
                    "lan_ip_max_count": 2,
                },
                "temperature": {
                    "use_fahrenheit": False,
                },
            },
            clear=True,
        ), tempfile.TemporaryDirectory() as temp_dir:
            # We create a fake temporary configuration file.
            with open(
                os.path.join(temp_dir, "config.json"), mode="w", encoding="UTF-8"
            ) as f_config:
                f_config.write(
                    """\
{
    "allow_overriding": false,
    "suppress_warnings": true,
    "colors_palette": {
        "use_unicode": false
    },
    "ip_settings": {
        "lan_ip_max_count": 4
    },
    "temperature": {
        "use_fahrenheit": true
    }
}
"""
                )

            # Let's load it into our `Configuration` instance.
            configuration._load_configuration(temp_dir)  # pylint: disable=protected-access

            # Let's check the result :S
            self.assertDictEqual(
                configuration._config,  # pylint: disable=protected-access
                {
                    "allow_overriding": False,
                    "suppress_warnings": True,
                    "colors_palette": {
                        "use_unicode": False,
                    },
                    "ip_settings": {
                        "lan_ip_max_count": 4,
                    },
                    "temperature": {
                        "use_fahrenheit": True,
                    },
                },
            )
            # The logging level has changed due to the `suppress_warnings` option being set.
            self.assertEqual(logging.getLogger().getEffectiveLevel(), logging.ERROR)

            # Let's try to load the `config.json` file present in this project.
            configuration._load_configuration("archey/")  # pylint: disable=protected-access

            # It should not happen as `allow_overriding` has been set to false.
            # Thus, the configuration is supposed to be the same as before.
            self.assertDictEqual(
                configuration._config,  # pylint: disable=protected-access
                {
                    "allow_overriding": False,
                    "suppress_warnings": True,
                    "colors_palette": {
                        "use_unicode": False,
                    },
                    "ip_settings": {
                        "lan_ip_max_count": 4,
                    },
                    "temperature": {
                        "use_fahrenheit": True,
                    },
                },
            )

    def test_instantiation_config_path(self):
        """Test for configuration loading from specific user-defined path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # We create a fake temporary configuration file.
            config_file = os.path.join(temp_dir, "user.cfg")  # A pure arbitrary name.
            with open(config_file, mode="w", encoding="UTF-8") as f_config:
                f_config.write(
                    """\
{
    "allow_overriding": false,
    "suppress_warnings": true,
    "colors_palette": {
        "use_unicode": false
    },
    "ip_settings": {
        "lan_ip_max_count": 4
    },
    "temperature": {
        "use_fahrenheit": true
    }
}
"""
                )

            configuration = Configuration(config_path=config_file)

            # We can't use `assertDictEqual` here as the resulting `_config` internal object
            #  directly depends on the default one (which constantly evolves).
            # We safely check that above entries have correctly been overridden.
            self.assertFalse(configuration.get("allow_overriding"))
            self.assertTrue(configuration.get("suppress_warnings"))
            self.assertFalse(configuration.get("colors_palette")["use_unicode"])
            self.assertEqual(configuration.get("ip_settings")["lan_ip_max_count"], 4)
            self.assertTrue(configuration.get("temperature")["use_fahrenheit"])

    def test__iter__(self):
        """Very simple method checking our `__iter__` implementation"""
        configuration = Configuration()
        self.assertEqual(
            configuration._config,  # pylint: disable=protected-access
            dict(configuration),
        )


if __name__ == "__main__":
    unittest.main()
