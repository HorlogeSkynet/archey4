"""Archey API module"""

from datetime import datetime

import json

from archey._version import __version__
from archey.colors import Colors


class API:
    """
    This class provides results serialization for external usages.
    At the moment, only JSON has been implemented.
    Feel free to contribute to add other formats as needed.
    """
    def __init__(self, results):
        self.results = results

    def json_serialization(self, pretty_print=False):
        """
        JSON serialization of results.
        Set `pretty_print` to `True` to enable output indentation.

        Note: For Python < 3.6, the keys order is not guaranteed.
        """
        document = {
            'data': {},
            'meta': {
                'version': self._version_to_semver_segments(__version__),
                'date': datetime.now().isoformat()
            }
        }
        for result in self.results:
            document['data'].setdefault(
                result[0], []
            ).append(
                Colors.remove_colors(result[1])
                if isinstance(result[1], str)
                else result[1]
            )

        return json.dumps(
            document,
            indent=(4 if pretty_print else None)
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
