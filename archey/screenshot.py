"""Simple module doing its best as taking a screenshot of the current screen"""

import os
import sys
import time

from contextlib import ExitStack
from datetime import datetime
from functools import partial
from subprocess import CalledProcessError, DEVNULL, check_call


def take_screenshot(output_file=None):
    """
    Simple function trying to take a screenshot using various famous back-end programs.
    When supported by the found and available back-end, try to honor `output_file`.
    """
    if not output_file or os.path.isdir(output_file):
        # When a directory is provided, we've to force `output_file` to represent a **file** path.
        output_file = os.path.join(
            (output_file or os.getcwd()),
            datetime.now().strftime('archey4_screenshot_%Y-%m-%d_%H.%M.%S.png')
        )

    # Some programs don't accept specific filename as parameters.
    # In such cases, we may provide them a target directory instead.
    output_dir = os.path.dirname(output_file)

    # Back-end programs that _may_ (?) be available across different platforms.
    screenshot_tools = {
        'Flameshot': ['flameshot', 'full', '-p', output_dir],
        'ImageMagick': ['import', '-window', 'root', output_file],
        'scrot': ['scrot', '-z', output_file],
        'Shutter': ['shutter', '-f', '-o', output_file, '-e'],
    }

    # Extends the original screenshot tools dictionary according to current platform.
    if sys.platform in ('win32', 'cygwin'):
        screenshot_tools['SnippingTool'] = ['SnippingTool.exe', '/clip']
    elif sys.platform == 'darwin':
        screenshot_tools['ScreenCapture'] = [
            'screencapture',
            '-x',
            '-t', output_file.rpartition('.')[2],
            output_file
        ]
    else:  # *NIX systems (and others)...
        screenshot_tools['Escrotum'] = ['escrotum', output_file]
        screenshot_tools['GNOME-Screenshot'] = ['gnome-screenshot', '-f', output_file]
        screenshot_tools['grim'] = ['grim', output_file]
        screenshot_tools['KDE-Spectacle'] = ['spectacle', '-b', '-o', output_file]
        screenshot_tools['Xfce4-Screenshooter'] = ['xfce4-screenshooter', '-f', '-s', output_dir]
        screenshot_tools['Screencap (Android)'] = [
            'screencap',  # Binary available on Android.
            '-p',         # It only accepts PNG as image output format.
            (output_file.rpartition('.')[0] + '.png')
        ]

    # This part purposefully blocks so we wait a little bit before taking the screenshot.
    # It prevents taking a screenshot before Archey's output has appeared.
    for time_remaining in range(3, 0, -1):
        taking_sc_str = 'Taking screenshot in {:1d}...'.format(time_remaining)
        print(taking_sc_str, end='', flush=True)
        time.sleep(1)
        print('\r' + ' ' * len(taking_sc_str), end='\r', flush=True)
    time.sleep(0.5)

    with ExitStack() as defer_stack:
        for screenshot_tool, screenshot_cmd in screenshot_tools.items():
            try:
                check_call(screenshot_cmd, stderr=DEVNULL)
            except FileNotFoundError:
                continue
            except CalledProcessError as process_error:
                defer_stack.callback(partial(
                    print,
                    'Couldn\'t take a screenshot with {}: \"{}\".'.format(
                        screenshot_tool, process_error
                    ),
                    file=sys.stderr
                ))
                continue
            break
        else:
            defer_stack.callback(partial(
                sys.exit,
                """\
Sorry, we couldn\'t find any supported program to take a screenshot on your system.
Please install one of the following and try again: {}.\
""".format(', '.join(screenshot_tools.keys()))))
