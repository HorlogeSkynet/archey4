"""Test module for Archey's CPU detection module"""

import unittest
from unittest.mock import MagicMock, call, mock_open, patch

from archey.configuration import DEFAULT_CONFIG
from archey.entries.cpu import CPU
from archey.test import CustomAssertions
from archey.test.entries import HelperMethods


class TestCPUEntry(unittest.TestCase, CustomAssertions):
    """
    Here, we mock the `open` call on `/proc/cpuinfo` with fake content.
    In some cases, `lscpu` output is being mocked too.
    """

    @patch(
        "archey.entries.cpu.open",
        mock_open(
            read_data="""\
processor\t: 0
vendor_id\t: CPU-VENDOR-NAME
cpu family\t: X
model\t\t: YY
model name\t: CPU-MODEL-NAME
physical id\t: 0
"""
        ),
    )
    def test_parse_proc_cpuinfo_one_entry(self):
        """Test `/proc/cpuinfo` parsing"""
        self.assertListEqual(
            CPU._parse_proc_cpuinfo(),  # pylint: disable=protected-access
            [{"CPU-MODEL-NAME": 1}],
        )

    @patch(
        "archey.entries.cpu.open",
        mock_open(
            read_data="""\
processor\t: 0
vendor_id\t: CPU-VENDOR-NAME
cpu family\t: X
model\t\t: YY
model name\t: CPU-MODEL-NAME
physical id\t: 0

processor\t: 1
vendor_id\t: CPU-VENDOR-NAME
cpu family\t: X
model\t\t: YY
model name\t: ANOTHER-CPU-MODEL
physical id\t: 1

processor\t: 2
vendor_id\t: CPU-VENDOR-NAME
cpu family\t: X
model\t\t: YY
model name\t: ANOTHER-CPU-MODEL
physical id\t: 1
"""
        ),
    )
    def test_parse_proc_cpuinfo_multiple_entries(self):
        """Test `/proc/cpuinfo` parsing"""
        self.assertListEqual(
            CPU._parse_proc_cpuinfo(),  # pylint: disable=protected-access
            [{"CPU-MODEL-NAME": 1}, {"ANOTHER-CPU-MODEL": 2}],
        )

    @patch(
        "archey.entries.cpu.open",
        mock_open(
            read_data="""\
processor\t: 0
vendor_id\t: CPU-VENDOR-NAME
cpu family\t: X
model\t\t: YY
model name\t: CPU-MODEL-NAME
physical id\t: 0

processor\t: 1
vendor_id\t: CPU-VENDOR-NAME
cpu family\t: X
model\t\t: YY
model name\t: CPU-MODEL-NAME
physical id\t: 1

processor\t: 2
vendor_id\t: CPU-VENDOR-NAME
cpu family\t: X
model\t\t: YY
model name\t: CPU-MODEL-NAME
physical id\t: 0

processor\t: 3
vendor_id\t: CPU-VENDOR-NAME
cpu family\t: X
model\t\t: YY
model name\t: CPU-MODEL-NAME
physical id\t: 1
"""
        ),
    )
    def test_parse_proc_cpuinfo_one_cpu_dual_socket(self):
        """Test `/proc/cpuinfo` parsing for same CPU model across two sockets"""
        self.assertListEqual(
            CPU._parse_proc_cpuinfo(),  # pylint: disable=protected-access
            [{"CPU-MODEL-NAME": 2}, {"CPU-MODEL-NAME": 2}],
        )

    @patch(
        "archey.entries.cpu.open",
        mock_open(
            read_data="""\
processor\t: 0
vendor_id\t: CPU-VENDOR-NAME
cpu family\t: X
model\t\t: YY
model name\t: CPU-MODEL-NAME
physical id\t: 0

processor\t: 1
vendor_id\t: CPU-VENDOR-NAME
cpu family\t: X
model\t\t: YY
model name\t: ANOTHER-CPU-MODEL
physical id\t: 0

processor\t: 2
vendor_id\t: CPU-VENDOR-NAME
cpu family\t: X
model\t\t: YY
model name\t: ANOTHER\tCPU   MODEL WITH STRANGE S P  A   C     E     S
physical id\t: 1

processor\t: 3
vendor_id\t: CPU-VENDOR-NAME
cpu family\t: X
model\t\t: YY
model name\t: ANOTHER\tCPU   MODEL WITH STRANGE S P  A   C     E     S
physical id\t: 1
"""
        ),
    )
    def test_parse_proc_cpuinfo_multiple_inconsistent_entries(self):
        """
        Test `/proc/cpuinfo` parsing with multiple CPUs sharing same physical ids (unlikely).
        Also check our model name normalizations applied on white characters.
        """
        self.assertListEqual(
            CPU._parse_proc_cpuinfo(),  # pylint: disable=protected-access
            [
                {"CPU-MODEL-NAME": 1, "ANOTHER-CPU-MODEL": 1},
                {"ANOTHER CPU MODEL WITH STRANGE S P A C E S": 2},
            ],
        )

    @patch("archey.entries.cpu.open", side_effect=PermissionError())
    def test_parse_proc_cpuinfo_unreadable_file(self, _):
        """Check behavior when `/proc/cpuinfo` could not be read from disk"""
        self.assertListEmpty(CPU._parse_proc_cpuinfo())  # pylint: disable=protected-access

    @patch(
        "archey.entries.cpu.check_output",
        side_effect=[
            FileNotFoundError(),
            """\
{
  "SPHardwareDataType" : [
    {
      "_name" : "hardware_overview",
      "cpu_type" : "Dual-Core Intel Core i5",
      "current_processor_speed" : "3,1 GHz",
      "machine_model" : "MacBookPro00OOooOO00",
      "machine_name" : "MacBook Pro",
      "number_processors" : 2,
      "packages" : 1,
      "platform_cpu_htt" : "htt_enabled",
      "platform_UUID" : "XXXXXXXX-YYYY-ZZZZ-TTTT-UUUUUUUUUUUU",
      "provisioning_UDID" : "XXXXXXXX-YYYY-ZZZZ-TTTT-UUUUUUUUUUUU",
      "serial_number" : "XX00YY11ZZ22"
    }
  ]
}
""",
        ],
    )
    def test_parse_system_profiler(self, _):
        """Check `_parse_system_profiler` behavior"""
        # pylint: disable=protected-access
        self.assertListEmpty(CPU._parse_system_profiler())
        self.assertListEqual(
            CPU._parse_system_profiler(),
            [{"Dual-Core Intel Core i5 @ 3.1 GHz": 4}],
        )
        # pylint: enable=protected-access

    @patch(
        "archey.entries.cpu.check_output",
        side_effect=[
            FileNotFoundError(),
            """\
Intel(R) Core(TM) i5-7267U CPU @ 3.10GHz
8
""",
        ],
    )
    def test_parse_sysctl_machdep(self, _):
        """Check `_parse_sysctl_machdep` behavior"""
        # pylint: disable=protected-access
        self.assertListEmpty(CPU._parse_sysctl_machdep())
        self.assertListEqual(
            CPU._parse_sysctl_machdep(),
            [{"Intel(R) Core(TM) i5-7267U CPU @ 3.10GHz": 8}],
        )
        # pylint: enable=protected-access

    @patch(
        "archey.entries.cpu.check_output",
        side_effect=[
            """\
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
CPU(s):              4
On-line CPU(s) list: 0-3
Thread(s) per core:  1
Core(s) per socket:  4
Socket(s):           1
NUMA node(s):        1
Vendor ID:           CPU-VENDOR-NAME
CPU family:          Z
Model:               \xde\xad\xbe\xef
Model name:          CPU-MODEL-NAME
""",
            """\
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
CPU(s):              2
On-line CPU(s) list: 0-1
Thread(s) per core:  1
Core(s) per socket:  2
Socket(s):           1
NUMA node(s):        1
Vendor ID:           CPU-VENDOR-NAME
CPU family:          Z
Model:               \xde\xad\xbe\xef
Model name:          CPU-MODEL-NAME

Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
CPU(s):              4
On-line CPU(s) list: 0-3
Thread(s) per core:  2
Core(s) per socket:  2
Socket(s):           1
NUMA node(s):        1
Vendor ID:           CPU-VENDOR-NAME
CPU family:          Z
Model:               \xde\xad\xbe\xef
Model name:          ANOTHER-CPU-MODEL
""",
            """\
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
CPU(s):              16
On-line CPU(s) list: 0-15
Thread(s) per core:  2
Core(s) per socket:  4
Socket(s):           2
NUMA node(s):        2
Vendor ID:           CPU-VENDOR-NAME
CPU family:          Z
Model:               \xde\xad\xbe\xef
Model name:          CPU-MODEL-NAME
""",
            """\
Architecture: aarch64
CPU op-mode(s): 32-bit, 64-bit
Byte Order: Little Endian
CPU(s): 4
On-line CPU(s) list: 0-3
Vendor ID: ARM
Model name: Cortex-A72
Model: 3
Thread(s) per core: 1
Core(s) per cluster: 4
Socket(s): -
Cluster(s): 1
""",
        ],
    )
    def test_parse_lscpu_output(self, _):
        """
        Test model name parsing from `lscpu` output.

        See issues #29 and #127 (ARM architectures).
        `/proc/cpuinfo` will not contain `model name` (nor `physical id`) info.
        `lscpu` output will be used instead.
        """
        with self.subTest("Simple unique CPU."):
            self.assertListEqual(
                CPU._parse_lscpu_output(),  # pylint: disable=protected-access
                [{"CPU-MODEL-NAME": 4}],
            )

        with self.subTest("Two CPUs, 1 socket."):
            self.assertListEqual(
                CPU._parse_lscpu_output(),  # pylint: disable=protected-access
                [{"CPU-MODEL-NAME": 2}, {"ANOTHER-CPU-MODEL": 4}],
            )

        with self.subTest("1 CPU, 2 sockets."):
            self.assertListEqual(
                CPU._parse_lscpu_output(),  # pylint: disable=protected-access
                [{"CPU-MODEL-NAME": 8}, {"CPU-MODEL-NAME": 8}],
            )

        with self.subTest("4 CPUs, 1 cluster."):
            self.assertListEqual(
                CPU._parse_lscpu_output(),  # pylint: disable=protected-access
                [{"Cortex-A72": 4}],
            )

    @HelperMethods.patch_clean_configuration
    def test_various_output_configuration(self):
        """Test `output` overloading based on user preferences combination"""
        cpu_instance_mock = HelperMethods.entry_mock(CPU)
        output_mock = MagicMock()

        cpu_instance_mock.value = [{"CPU-MODEL-NAME": 1}, {"ANOTHER-CPU-MODEL": 2}]

        with self.subTest("Single-line combined output."):
            cpu_instance_mock.options["one_line"] = True

            CPU.output(cpu_instance_mock, output_mock)
            output_mock.append.assert_called_once_with(
                "CPU", "CPU-MODEL-NAME, 2 x ANOTHER-CPU-MODEL"
            )

        output_mock.reset_mock()

        with self.subTest("Single-line combined output (no count)."):
            cpu_instance_mock.options["show_cores"] = False
            cpu_instance_mock.options["one_line"] = True

            CPU.output(cpu_instance_mock, output_mock)
            output_mock.append.assert_called_once_with("CPU", "CPU-MODEL-NAME, ANOTHER-CPU-MODEL")

        output_mock.reset_mock()

        with self.subTest("Multi-lines output (with counts)."):
            cpu_instance_mock.options["show_cores"] = True
            cpu_instance_mock.options["one_line"] = False

            CPU.output(cpu_instance_mock, output_mock)
            self.assertEqual(output_mock.append.call_count, 2)
            output_mock.append.assert_has_calls(
                [call("CPU", "CPU-MODEL-NAME"), call("CPU", "2 x ANOTHER-CPU-MODEL")]
            )

        output_mock.reset_mock()

        with self.subTest("No CPU detected output."):
            cpu_instance_mock.value = []

            CPU.output(cpu_instance_mock, output_mock)
            output_mock.append.assert_called_once_with(
                "CPU", DEFAULT_CONFIG["default_strings"]["not_detected"]
            )

    @patch(
        "archey.entries.cpu.check_output",
        side_effect=[
            FileNotFoundError(),
            """\
Intel(R) Core(TM) i5-5300U CPU @ 2.30GHz
4
""",
        ],
    )
    def test_parse_sysctl_cpu_model(self, _):
        """Check `_parse_sysctl_cpu_model` behavior"""
        # pylint: disable=protected-access
        self.assertListEmpty(CPU._parse_sysctl_cpu_model())
        self.assertListEqual(
            CPU._parse_sysctl_machdep(),
            [{"Intel(R) Core(TM) i5-5300U CPU @ 2.30GHz": 4}],
        )
        # pylint: enable=protected-access


if __name__ == "__main__":
    unittest.main()
