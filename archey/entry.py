"""Entry base class"""

import logging
from abc import ABC as AbstractBaseClass
from abc import abstractmethod
from typing import List, Optional, TypeAlias

from archey.configuration import Configuration


class Entry(AbstractBaseClass):
    """Module base class"""

    ValueType: TypeAlias = List["tuple[str, str]"]
    _ICON: Optional[str] = None
    _PRETTY_NAME: Optional[str] = None

    def __new__(cls, *_, **kwargs):
        """Hook object instantiation to handle our particular `disabled` config field"""
        if kwargs.get("options", {}).pop("disabled", False):
            return None

        return super().__new__(cls)

    @abstractmethod
    def __init__(self, name: Optional[str] = None, value=None, options: Optional[dict] = None):
        configuration = Configuration()

        # Each entry will have always have the following attributes...
        # `name`: key (defaults to the instantiated entry class name);
        # `value`: value of entry as an appropriate object;
        # `options`: configuration options *specific* to an entry instance;
        self.name = name or self._PRETTY_NAME or self.__class__.__name__
        self.value = value
        self.options = options or {}

        # optionally prepend entry name with an icon
        icon = self.options.get("icon", self._ICON)
        if icon is not None and configuration.get("entries_icon"):
            self.name = f"{icon} {self.name}"

        # Propagates a reference to default strings specified in `Configuration`.
        self._default_strings = configuration.get("default_strings")

        # Provision a logger for each entry.
        self._logger = logging.getLogger(self.__module__)

    def __str__(self) -> str:
        """Provide a sane default printable string representation of the entry"""
        # Assume that the `__str__` of our value is usable
        return str(self.value)

    @property
    def pretty_value(self) -> ValueType:
        """
        Provide a "pretty" value. Can be overridden by subclasses.
        Return value is a list (1 object per line) of tuples of (name, value).
        """
        if self.value:
            # Let's assume we can just use `__str__` on ourself,
            # and create a single-line output with it.
            return [(self.name, str(self))]
        # If the value is "falsy" leave a generic "Not detected" message for this entry.
        return [(self.name, self._default_strings.get("not_detected"))]
