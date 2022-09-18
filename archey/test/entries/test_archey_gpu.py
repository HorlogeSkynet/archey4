"""Test module for Archey's GPU detection module"""

import unittest
from unittest.mock import MagicMock, call, patch

from archey.configuration import DEFAULT_CONFIG
from archey.entries.gpu import GPU
from archey.test import CustomAssertions
from archey.test.entries import HelperMethods


class TestGPUEntry(unittest.TestCase, CustomAssertions):
    """Here, we mock the `check_output` call to `lspci` to test the logic"""

    @patch(
        "archey.entries.gpu.check_output",
        side_effect=[
            FileNotFoundError(),
            """\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H VGA compatible controller: GPU-MODEL-NAME
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
""",
            """\
XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H VGA compatible controller: GPU-MODEL-NAME
XX:YY.H Display controller: ANOTHER-MATCHING-VIDEO-CONTROLLER
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
XX:YY.H 3D controller: 3D GPU-MODEL-NAME TAKES ADVANTAGE
""",
        ],
    )
    def test_parse_lspci_output(self, _):
        """Check `_parse_lspci_output` behavior"""
        # pylint: disable=protected-access
        self.assertListEmpty(GPU._parse_lspci_output())
        self.assertListEqual(GPU._parse_lspci_output(), ["GPU-MODEL-NAME"])
        self.assertListEqual(
            GPU._parse_lspci_output(),
            [
                "3D GPU-MODEL-NAME TAKES ADVANTAGE",
                "GPU-MODEL-NAME",
                "ANOTHER-MATCHING-VIDEO-CONTROLLER",
            ],
        )
        # pylint: enable=protected-access

    @patch(
        "archey.entries.gpu.check_output",
        side_effect=[
            FileNotFoundError(),
            """\
Intel HD Graphics 530:

  Chipset Model: Intel HD Graphics 530
  Type: GPU
  Bus: Built-In
  VRAM (Dynamic, Max): 1536 MB
  Vendor: Intel
  Device ID: 0x191b
  Revision ID: 0x0006
  Automatic Graphics Switching: Supported
  gMux Version: 4.0.29 [3.2.8]
  Metal: Supported, feature set macOS GPUFamily2 v1
  Displays:
    Color LCD:
      Display Type: Built-In Retina LCD
      Resolution: 2880 x 1800 Retina
      Framebuffer Depth: 24-Bit Color (ARGB8888)
      Main Display: Yes
      Mirror: Off
      Online: Yes
      Rotation: Supported
      Automatically Adjust Brightness: No

Radeon Pro 450:

  Chipset Model: AMD Radeon Pro 450
  Type: GPU
  Bus: PCIe
  PCIe Lane Width: x8
  VRAM (Total): 2 GB
  Vendor: AMD (0x1002)
  Device ID: 0x67ef
  Revision ID: 0x00ef
  ROM Revision: 113-C980AF-908
  VBIOS Version: 113-C9801AL-028
  EFI Driver Version: 01.A0.908
  Automatic Graphics Switching: Supported
  gMux Version: 4.0.29 [3.2.8]
  Metal: Supported, feature set macOS GPUFamily2 v1
""",
        ],
    )
    def test_parse_system_profiler(self, _):
        """Check `_parse_system_profiler` behavior"""
        # pylint: disable=protected-access
        self.assertListEmpty(GPU._parse_system_profiler())
        self.assertListEqual(
            GPU._parse_system_profiler(),
            ["Intel HD Graphics 530", "AMD Radeon Pro 450"],
        )
        # pylint: enable=protected-access

    @patch(
        "archey.entries.gpu.check_output",
        side_effect=[
            FileNotFoundError(),
            """\
vgapci0@pci0:0:1:0:   class=0x030000 card=0x21f617aa chip=0x01668086 rev=0x09 hdr=0x00
    vendor     = 'Intel Corporation'
    device     = '3rd Gen Core processor Graphics Controller'
    class      = display
    subclass   = VGA
hostb0@pci0:0:1:2:    class=0x060000 card=0x00000000 chip=0x12378086 rev=0x02 hdr=0x00
    vendor     = 'Intel Corporation'
    device     = '82440/1FX 440FX (Natoma) System Controller'
    class      = bridge
    subclass   = HOST-PCI
isab0@pci0:0:1:4:     class=0x060100 card=0x00000000 chip=0x70008086 rev=0x00 hdr=0x00
    vendor     = 'Intel Corporation'
    device     = 'PIIX3 PCI-to-ISA Bridge (Triton II) (82371SB)'
    class      = bridge
    subclass   = PCI-ISA
atapci0@pci0:0:1:6:   class=0x01018a card=0x00000000 chip=0x71118086 rev=0x01 hdr=0x00
    vendor     = 'Intel Corporation'
    device     = 'PIIX4/4E/4M IDE Controller (82371AB/EB/MB)'
    class      = mass storage
    subclass   = ATA
vgapci0@pci0:1:0:0:   class=0x030000 card=0x84391043 chip=0x0fc610de rev=0xa1 hdr=0x00
    vendor     = 'NVIDIA Corporation'
    device     = 'GK107 [GeForce GTX 650]'
    class      = display
    subclass   = VGA
bge0@pci0:1:0:2:      class=0x020000 card=0x2133103c chip=0x165f14e4 rev=0x00 hdr=0x00
    vendor     = 'Broadcom Corporation'
    device     = 'NetXtreme BCM5720 Gigabit Ethernet PCIe'
    class      = network
    subclass   = ethernet
none1@pci0:14:0:0:    class=0x0c0330 card=0x1996103c chip=0x00141912 rev=0x03 hdr=0x00
    vendor     = 'Renesas Technology Corp.'
    class      = serial bus
    subclass   = USB
vgapci0@pci0:16:0:0:  class=0x030000 card=0x3381103c chip=0x0533102b rev=0x00 hdr=0x00
    vendor     = 'Matrox Graphics, Inc.'
    device     = 'MGA G200EH'
    class      = display
    subclass   = VGA
""",
        ],
    )
    def test_parse_pciconf_output(self, _):
        """Check `_parse_pciconf_output` behavior"""
        # pylint: disable=protected-access
        self.assertListEmpty(GPU._parse_pciconf_output())
        self.assertListEqual(
            GPU._parse_pciconf_output(),
            [
                "Intel Corporation 3rd Gen Core processor Graphics Controller",
                "NVIDIA Corporation GK107 [GeForce GTX 650]",
                "Matrox Graphics, Inc. MGA G200EH",
            ],
        )
        # pylint: enable=protected-access

    @HelperMethods.patch_clean_configuration
    def test_various_output_configuration(self):
        """Test `output` overloading based on user preferences"""
        gpu_instance_mock = HelperMethods.entry_mock(GPU)
        output_mock = MagicMock()

        gpu_instance_mock.value = [
            "3D GPU-MODEL-NAME TAKES ADVANTAGE",
            "GPU-MODEL-NAME",
            "ANOTHER-MATCHING-VIDEO",
        ]

        with self.subTest("Single-line combined output."):
            gpu_instance_mock.options["one_line"] = True

            GPU.output(gpu_instance_mock, output_mock)
            output_mock.append.assert_called_once_with(
                "GPU", "3D GPU-MODEL-NAME TAKES ADVANTAGE, GPU-MODEL-NAME, ANOTHER-MATCHING-VIDEO"
            )

        output_mock.reset_mock()

        with self.subTest("Multi-lines output."):
            gpu_instance_mock.options["one_line"] = False

            GPU.output(gpu_instance_mock, output_mock)
            self.assertEqual(output_mock.append.call_count, 3)
            output_mock.append.assert_has_calls(
                [
                    call("GPU", "3D GPU-MODEL-NAME TAKES ADVANTAGE"),
                    call("GPU", "GPU-MODEL-NAME"),
                    call("GPU", "ANOTHER-MATCHING-VIDEO"),
                ]
            )

        output_mock.reset_mock()

        with self.subTest("No GPU detected output."):
            gpu_instance_mock.value = []

            GPU.output(gpu_instance_mock, output_mock)
            output_mock.append.assert_called_once_with(
                "GPU", DEFAULT_CONFIG["default_strings"]["not_detected"]
            )


if __name__ == "__main__":
    unittest.main()
