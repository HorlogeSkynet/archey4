"""Archey API module"""

from datetime import datetime

import json

from archey._version import __version__


class API:
    """
    This class provides results serialization for external usages.
    At the moment, only JSON has been implemented.
    Feel free to contribute to add other formats as needed.
    """
    def __init__(self, entries):
        self.entries = entries

    def json_serialization(self, indent=None):
        """
        JSON serialization of entries.
        Set `indent` to the number of wanted output indentation tabs (2-space long).

        Note: For Python < 3.6, the keys order is not guaranteed.
        """
        document = {
            'data': {},
            'meta': {
                'version': self._version_to_semver_segments(__version__),
                'date': datetime.now().isoformat(),
                'count': len(self.entries)
            }
        }
        for entry in self.entries:
            document['data'][entry.name] = entry.value

        return json.dumps(
            document,
            indent=((indent * 2) or None)
        )

    @staticmethod
    def _version_to_semver_segments(version):
        """Transforms string `version` to a tuple containing SemVer segments"""
        return tuple(
            map(
                int,
                version.lstrip('v').partition('-')[0].split('.')
            )
        )
