"""Simple module doing its best at taking a screenshot of the current screen"""

import logging
import os
import platform
import time
import typing
from contextlib import ExitStack
from datetime import datetime
from functools import partial
from subprocess import DEVNULL, CalledProcessError, check_call


def take_screenshot(output_file: typing.Optional[str] = None) -> bool:
    """
    Simple function trying to take a screenshot using various famous back-end programs.
    When supported by a found and available back-end, **try to** honor `output_file`.
    Returns a `bool` representing whether or not a screenshot could be taken.
    """
    if output_file is None or os.path.isdir(output_file):
        # When a directory is provided, we've to force `output_file` to represent a **file** path.
        output_file = os.path.join(
            (output_file or os.getcwd()),
            datetime.now().strftime("archey4_screenshot_%Y-%m-%d_%H.%M.%S.png"),
        )

    # Some programs don't accept specific filename as parameters.
    # In such cases, we may provide them a target directory instead.
    output_dir = os.path.dirname(output_file)

    # Back-end programs that _may_ (?) be available across different platforms.
    screenshot_tools = {
        "Flameshot": ["flameshot", "full", "-p", output_dir],
        "ImageMagick": ["import", "-window", "root", output_file],
        "maim": ["maim", output_file],
        "scrot": ["scrot", "-z", output_file],
        "Shutter": ["shutter", "-f", "-o", output_file, "-e"],
    }

    # Extends the original screenshot tools dictionary according to current platform.
    if platform.system() == "Windows":
        screenshot_tools["SnippingTool"] = ["SnippingTool.exe", "/clip"]
    elif platform.system() == "Darwin":
        screenshot_tools["ScreenCapture"] = [
            "screencapture",
            "-x",
            "-t",
            output_file.rpartition(".")[2],
            output_file,
        ]
    else:  # *NIX systems (and others)...
        screenshot_tools["Escrotum"] = ["escrotum", output_file]
        screenshot_tools["GNOME-Screenshot"] = ["gnome-screenshot", "-f", output_file]
        screenshot_tools["grim"] = ["grim", output_file]
        screenshot_tools["KDE-Spectacle"] = ["spectacle", "-b", "-o", output_file]
        screenshot_tools["Xfce4-Screenshooter"] = ["xfce4-screenshooter", "-f", "-s", output_dir]
        screenshot_tools["Screencap (Android)"] = [
            "screencap",  # Binary available on Android.
            "-p",  # It only accepts PNG as image output format.
            (output_file.rpartition(".")[0] + ".png"),
        ]

    # This part purposefully blocks so we wait a little bit before taking the screenshot.
    # It prevents taking a screenshot before Archey's output has appeared.
    for time_remaining in range(3, 0, -1):
        taking_sc_str = f"Taking screenshot in {time_remaining:1d}..."
        print(taking_sc_str, end="", flush=True)
        time.sleep(1)
        print("\r" + " " * len(taking_sc_str), end="\r", flush=True)
    time.sleep(0.5)

    with ExitStack() as defer_stack:
        for screenshot_tool, screenshot_cmd in screenshot_tools.items():
            try:
                check_call(screenshot_cmd, stderr=DEVNULL)
            except OSError:
                continue
            except CalledProcessError as process_error:
                defer_stack.callback(
                    partial(
                        logging.warning,
                        'Couldn\'t take a screenshot with %s: "%s".',
                        screenshot_tool,
                        process_error,
                    )
                )
                continue

            return True

    logging.error(
        """\
Sorry, we couldn\'t find any supported program to take a screenshot on your system.
Please install one of the following and try again: %s.""",
        ", ".join(screenshot_tools.keys()),
    )
    return False
