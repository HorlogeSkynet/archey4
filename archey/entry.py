"""Entry base class"""

import logging
from abc import ABC as AbstractBaseClass
from abc import abstractmethod
from typing import Any, Iterator, Optional, Tuple, TypeVar

from archey.configuration import Configuration

Self = TypeVar("Self", bound="Entry")


class Entry(AbstractBaseClass):
    """Module base class"""

    ValueType = Tuple[str, Optional[str]]
    _ICON: Optional[str] = None
    _PRETTY_NAME: Optional[str] = None

    def __new__(cls, *_, **kwargs):
        """Hook object instantiation to handle our particular `disabled` config field"""
        if kwargs.get("options", {}).pop("disabled", False):
            return None

        return super().__new__(cls)

    @abstractmethod
    def __init__(
        self: Self, name: Optional[str] = None, value=None, options: Optional[dict] = None
    ):
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

        # Create a default iterable & index
        self._iter_idx = 0
        self._iter_value: Iterator[Any] = iter([])

    def __iter__(self: Self) -> Self:
        """Best-effort set up of an iterable of value for inherited entries to use."""
        if isinstance(self.value, (str, int)):
            self._iter_value = iter([self.value])
        elif isinstance(self.value, dict):
            self._iter_value = iter(self.value.items())
        elif self.value:
            # Don't know what it is -- let `iter` deal with it.
            self._iter_value = iter(self.value)
        else:
            # Make an empty iterable rather than `[None]`
            self._iter_value = iter([])
        return self

    def __next__(self: Self) -> ValueType:
        """
        Default behaviour: assume we can just use `__str__` on ourself for a single-line output.
        """
        if self._iter_idx > 0:
            raise StopIteration

        self._iter_idx += 1
        # If the value is "truthy" use `__str__`
        if self.value:
            return (self.name, str(self))
        # Otherwise, just raise `StopIteration` immediately
        raise StopIteration

    def __str__(self: Self) -> str:
        """Provide a sane default printable string representation of the entry"""
        # Assume that the `__str__` of our value is usable
        return str(self.value)
