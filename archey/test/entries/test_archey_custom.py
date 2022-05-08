"""Test module for Archey custom entry module"""

import unittest
from unittest.mock import MagicMock, call

from archey.configuration import DEFAULT_CONFIG
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

    def test_multiple_lines_command_output(self) -> None:
        """Check multiple lines command output"""
        custom = Custom(
            options={
                "shell": True,
                "command": "echo 'Model 1'; echo 'Model 2'",
            }
        )
        self.assertListEqual(custom.value, ["Model 1", "Model 2"])

        output_mock = MagicMock()

        with self.subTest("Single-line combined output."):
            custom.options["one_line"] = True

            custom.output(output_mock)

            output_mock.append.assert_called_once_with("Custom", "Model 1, Model 2")

        output_mock.reset_mock()

        with self.subTest("Multi-lines combined output."):
            custom.options["one_line"] = False

            custom.output(output_mock)

            self.assertEqual(output_mock.append.call_count, 2)
            output_mock.append.assert_has_calls(
                [
                    call("Custom", "Model 1"),
                    call("Custom", "Model 2"),
                ]
            )

        output_mock.reset_mock()

        with self.subTest("No detected output."):
            custom.value = []

            custom.output(output_mock)

            output_mock.append.assert_called_once_with(
                "Custom",
                DEFAULT_CONFIG["default_strings"]["not_detected"],
            )

        output_mock.reset_mock()


if __name__ == "__main__":
    unittest.main()
