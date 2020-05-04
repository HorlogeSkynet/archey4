"""Entry base class"""

from abc import ABC as AbstractBaseClass, abstractmethod

from archey.configuration import Configuration


class Entry(AbstractBaseClass):
    """Module base class"""
    @abstractmethod
    def __init__(self, name=None, value=None):
        # Each entry will have `name` (key) and `value` attributes.
        # `None` by default.
        self.name = name
        self.value = value

        # Propagates a reference to `Configuration` singleton to each inheriting class.
        self._configuration = Configuration()

    def output(self, output):
        """Output the results to output. Can be overridden by subclasses."""
        output.append(self.name, self.value)
