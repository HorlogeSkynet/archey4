"""Entry base class"""

from abc import ABC as AbstractBaseClass, abstractmethod

from archey.configuration import Configuration


class Entry(AbstractBaseClass):
    """Module base class"""
    @abstractmethod
    def __init__(self, name=None, value=None, format_to_json=None):
        # Each entry will have always have the following attributes:
        # `name` (key); `value`; `_format_to_json`
        # (all `None` by default)
        self.name = name
        self.value = value
        # Non-entries won't need this attribute, so let's make it "internal":
        self._format_to_json = format_to_json

        # Propagates a reference to `Configuration` singleton to each inheriting class.
        self._configuration = Configuration()

    def output(self, output):
        """Output the results to output. Can be overridden by subclasses."""
        output.append(self.name, self.value)
