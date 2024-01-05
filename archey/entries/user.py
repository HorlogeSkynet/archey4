"""User session detection class"""

import getpass

from archey.configuration import Configuration
from archey.entry import Entry


class User(Entry):
    # Icons

    configuration = Configuration()
    icon = configuration.get("icon")

    if icon == True:
        _PRETTY_NAME = "\uf007 User"

    """Retrieves the session name of the current logged in user"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.value = getpass.getuser()
        except ImportError:
            # From <https://github.com/python/cpython/blob/3.9/Lib/getpass.py#L167>,
            #  `pwd` module import _might_ fail.
            pass
