"""Test module for Archey custom entry module"""

import os
import stat
import unittest
from unittest.mock import patch

from archey.configuration import Configuration
from archey.entries.custom import Custom


class TestCustomEntry(unittest.TestCase):
    """Custom entry unit test cases"""

    def test_program_execution(self) -> None:
        """Check program execution behavior"""
        custom = Custom(
            options={
                "command": ["echo", "my output"],
            }
        )
        self.assertListEqual(custom.value, ["my output"])

    def test_shell_command(self) -> None:
        """Check shell command behavior"""
        custom = Custom(
            options={
                "shell": True,
                "command": "export TEST='my output'; echo \"$TEST\"",
            }
        )
        self.assertListEqual(custom.value, ["my output"])

    def test_error_shell_command(self) -> None:
        """Check error shell command behavior"""
        custom = Custom(
            options={
                "command": ["false"],
            }
        )
        self.assertIsNone(custom.value, None)

    def test_ignored_error_shell_command(self) -> None:
        """Check ignored error shell command behavior"""
        custom = Custom(
            options={
                "shell": True,
                "command": "echo 'my output' && false",
                "check": False,
            }
        )
        self.assertListEqual(custom.value, ["my output"])

    def test_silenced_shell_command(self) -> None:
        """Check silenced shell command behavior"""
        custom = Custom(
            options={
                "shell": True,
                "command": "echo 'my output' > /dev/stderr",
                "log_stderr": False,
            }
        )
        self.assertIsNone(custom.value, None)

    def test_output(self) -> None:
        """Check command output"""
        custom = Custom(
            options={
                "shell": True,
                "command": "echo 'Model 1'; echo 'Model 2'",
            }
        )
        self.assertListEqual(custom.value, ["Model 1", "Model 2"])

        with self.subTest("Normal output."):
            custom.options["one_line"] = False
            self.assertListEqual(
                list(custom),
                [
                    ("Custom", "Model 1"),
                    ("Custom", "Model 2"),
                ],
            )

        with self.subTest("No detected output."):
            custom.value = []
            self.assertListEqual(
                list(custom),
                [],
            )

    def test_unsafe_config_files(self):
        """Check unsafe configuration files lead to Custom entry loading prevention"""
        configuration = Configuration()
        with self.subTest("System-wide, owned by root with strict permissions."), patch.dict(
            configuration._config_files_info,  # pylint: disable=protected-access
            {
                "/etc/archey4/config.json": os.stat_result(
                    (stat.S_IFREG | 0o644, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                ),
            },
        ):
            self.assertIsNotNone(Custom(options={"command": ["true"]}))

        with self.subTest("System-wide, owned by root with broad permissions."), patch.dict(
            configuration._config_files_info,  # pylint: disable=protected-access
            {
                "/etc/archey4/config.json": os.stat_result(
                    (stat.S_IFREG | 0o666, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                ),
            },
        ):
            self.assertIsNone(Custom(options={"command": ["true"]}))

        with self.subTest("User preferences, owned by user with broad permissions."), patch(
            "archey.entries.custom.os.geteuid", return_value=1000
        ), patch.dict(
            configuration._config_files_info,  # pylint: disable=protected-access
            {
                "/etc/archey4/config.json": os.stat_result(
                    (stat.S_IFREG | 0o644, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                ),
                "/home/user/.config/archey4/config.json": os.stat_result(
                    (stat.S_IFREG | 0o664, 0, 0, 0, 1000, 1000, 0, 0, 0, 0)
                ),
            },
        ):
            self.assertIsNone(Custom(options={"command": ["true"]}))

        with self.subTest(
            "Specific preferences, owned by another user with strict permissions."
        ), patch("archey.entries.custom.os.geteuid", return_value=1000), patch.dict(
            configuration._config_files_info,  # pylint: disable=protected-access
            {
                "/tmp/archey4/config.json": os.stat_result(
                    (stat.S_IFREG | 0o644, 0, 0, 0, 1001, 1001, 0, 0, 0, 0)
                ),
            },
        ):
            self.assertIsNone(Custom(options={"command": ["true"]}))

        with self.subTest(
            "Specific preferences, owned by another user on a platform without GETEUID."
        ), patch("archey.entries.custom.os.geteuid", None), patch.dict(
            configuration._config_files_info,  # pylint: disable=protected-access
            {
                "/tmp/archey4/config.json": os.stat_result(
                    (stat.S_IFREG | 0o644, 0, 0, 0, 1001, 1001, 0, 0, 0, 0)
                ),
            },
        ):
            self.assertIsNotNone(Custom(options={"command": ["true"]}))


if __name__ == "__main__":
    unittest.main()
