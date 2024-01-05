"""Processes entry class"""

from archey.entry import Entry
from archey.processes import Processes as ProcessesUtil
from archey.configuration import Configuration


class Processes(Entry):

    # Icons

    configuration = Configuration()
    icon = configuration.get("icon")

    if icon == True:
        _PRETTY_NAME = "\ueba2 Processes"

    """
    Simple wrapper to `archey.processes` to provide the number of running processes as an entry.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value = ProcessesUtil().number
