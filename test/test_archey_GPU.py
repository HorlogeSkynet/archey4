
import os
import tempfile
import unittest
from unittest.mock import patch

from archey.archey import GPU


class TestGPUEntry(unittest.TestCase):
    """
    Here, we mock the `Popen` call to `lspci` to test the `grep` call.
    More information about the method here :
    <https://horlogeskynet.github.io/blog/programming/how-to-mock-stdout-runtime-attribute-of-subprocess-popen-in-python-3>
    """

    def setUp(self):
        self.stdout_mock = tempfile.NamedTemporaryFile(delete=False)

    def tearDown(self):
        self.stdout_mock.close()
        os.remove(self.stdout_mock.name)

    @patch('archey.archey.Popen')
    def test_match_VGA(self, popen_mock):
        self.stdout_mock.write(b"""XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H VGA compatible controller: GPU-MODEL-NAME
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
""")
        self.stdout_mock.seek(0)
        popen_mock.return_value.stdout = self.stdout_mock

        self.assertEqual(GPU().value, 'GPU-MODEL-NAME')

    @patch('archey.archey.Popen')
    def test_match_Display_longer_than_48_characters(self, popen_mock):
        self.stdout_mock.write(b"""XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
XX:YY.H Display controller: GPU-MODEL-NAME VERY LONG WITH SPACES TO BE CUT OFF
""")
        self.stdout_mock.seek(0)
        popen_mock.return_value.stdout = self.stdout_mock

        self.assertEqual(
            GPU().value,
            'GPU-MODEL-NAME VERY LONG WITH SPACES TO BE...'
        )

    @patch('archey.archey.Popen')
    def test_multimatches_3D_and_Display(self, popen_mock):
        self.stdout_mock.write(b"""XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H 3D controller: FIRST GPU-MODEL-NAME TAKES ADVANTAGE
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
XX:YY.H Display controller: ANOTHER MATCHING VIDEO CONTROLLER IGNORED
""")
        self.stdout_mock.seek(0)
        popen_mock.return_value.stdout = self.stdout_mock

        self.assertEqual(
            GPU().value,
            'FIRST GPU-MODEL-NAME TAKES ADVANTAGE'
        )

    @patch('archey.archey.Popen')
    @patch.dict(
        'archey.archey.config.config',
        {'default_strings': {'not_detected': 'Not detected'}}
    )
    def test_no_match(self, popen_mock):
        self.stdout_mock.write(b"""XX:YY.H IDE interface: IIIIIIIIIIIIIIII
XX:YY.H SMBus: BBBBBBBBBBBBBBBB
XX:YY.H Audio device: DDDDDDDDDDDDDDDD
""")
        self.stdout_mock.seek(0)
        popen_mock.return_value.stdout = self.stdout_mock

        self.assertEqual(GPU().value, 'Not detected')


if __name__ == '__main__':
    unittest.main()
