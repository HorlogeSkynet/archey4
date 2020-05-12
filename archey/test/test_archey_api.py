"""Test module for `archey.api`"""

import json
import unittest

from archey.api import API


class TestApiUtil(unittest.TestCase):
    """
    Simple test cases to check `API` formatting behaviors.
    """
    def test_json_serialization(self):
        """
        Check that our JSON serialization is working as expected.
        """
        api_instance = API([
            ('simple', 'test'),
            ('some', 'more'),
            ('simple', 42),
            ('simple', '\x1b[31m???\x1b[0m')
        ])

        output_json_document = json.loads(api_instance.json_serialization())
        self.assertDictEqual(
            output_json_document['data'],
            {
                'simple': [
                    'test',
                    42,
                    '???'
                ],
                'some': ['more']
            }
        )
        self.assertIn('meta', output_json_document)
        for semver_segment in output_json_document['meta']['version']:
            self.assertTrue(isinstance(semver_segment, int))

    def test_version_to_semver_segments(self):
        """Check `_version_to_semver_segments` implementation behavior"""
        self.assertTupleEqual(
            API._version_to_semver_segments('v1.2.3'),  # pylint: disable=protected-access
            (1, 2, 3)
        )
        self.assertTupleEqual(
            API._version_to_semver_segments('1.2.3.4-beta5'),  # pylint: disable=protected-access
            (1, 2, 3, 4)
        )
        self.assertTupleEqual(
            API._version_to_semver_segments('1'),  # pylint: disable=protected-access
            (1,)
        )
