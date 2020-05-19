"""Test module for `archey.api`"""

from datetime import datetime

import json
import unittest
from unittest.mock import Mock

from archey.api import API


class TestApiUtil(unittest.TestCase):
    """
    Simple test cases to check `API` formatting behaviors.
    """
    def test_json_serialization(self):
        """
        Check that our JSON serialization is working as expected.
        """
        mocked_entries = [
            Mock(value='test'),
            Mock(value='more'),
            Mock(value=42),
            Mock(
                value={
                    'complex': {
                        'dictionary': True
                    }
                }
            )
        ]

        # Since we can't assign a Mock's `name` attribute on creation, we'll do it here.
        # Note: Since each entry is only present once, all `name` attributes are always unique.
        for idx, name in enumerate(('simple1', 'some', 'simple2', 'simple3')):
            mocked_entries[idx].name = name

        api_instance = API(mocked_entries)
        json_serialization = api_instance.json_serialization(
            # Imitates an execution with `-jjj`.
            indent=2
        )
        output_json_document = json.loads(json_serialization)

        # Indentation verification (all bar first and last lines must begin with two tabs).
        self.assertTrue(
            all(line.startswith('    ') for line in json_serialization.splitlines()[1:-2])
        )

        # Output data verifications.
        self.assertIn('data', output_json_document)
        self.assertDictEqual(
            output_json_document['data'],
            {
                'simple1': 'test',
                'some': 'more',
                'simple2': 42,
                'simple3': {
                    'complex': {
                        'dictionary': True
                    }
                }
            }
        )

        # Meta-data verifications.
        self.assertIn('meta', output_json_document)
        # Check the SemVer segments types (should be integers).
        for semver_segment in output_json_document['meta']['version']:
            self.assertTrue(isinstance(semver_segment, int))
        # Check that generated `date` meta-data is correct and not in the future.
        self.assertGreaterEqual(
            datetime.now(),
            # `datetime.fromisoformat` is not available for Python < 3.7, so we parse it manually.
            #datetime.fromisoformat(output_json_document['meta']['date'])
            datetime.strptime(output_json_document['meta']['date'], "%Y-%m-%dT%H:%M:%S.%f")
        )
        # Check the `count` meta-data attribute.
        self.assertEqual(
            output_json_document['meta']['count'],
            4
        )

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
