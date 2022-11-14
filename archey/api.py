"""Archey API module"""

import json
from datetime import datetime
from typing import Sequence

from archey._version import __version__
from archey.distributions import Distributions
from archey.entry import Entry
from archey.utility import Utility


class API:
    """
    This class provides results serialization for external usages.
    At the moment, only JSON has been implemented.
    Feel free to contribute to add other formats as needed.
    """

    def __init__(self, entries: Sequence[Entry]):
        self.entries = entries

    def json_serialization(self, indent: int = 0) -> str:
        """
        JSON serialization of entries.
        Set `indent` to the number of wanted output indentation tabs (2-space long).
        """
        document = {
            "data": {entry.name: entry.value for entry in self.entries},
            "meta": {
                "version": Utility.version_to_semver_segments(__version__),
                "date": datetime.now().isoformat(),
                "count": len(self.entries),
                "distro": Distributions.get_local().value,
            },
        }

        return json.dumps(document, indent=((indent * 2) or None))
