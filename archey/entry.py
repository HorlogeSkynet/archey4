"""Entry base class"""

from abc import ABC as AbstractBaseClass

from archey.configuration import Configuration


class Entry(AbstractBaseClass):
    """Module base class"""
    def __init__(self):
        # Each entry will have `name` (key) and `value` attributes.
        # `None` by default.
        self.name = None
        self.value = None

        # Propagates a reference to `Configuration` singleton to each inheriting class.
        self._configuration = Configuration()

    def output(self, output):
        """Output the results to output. Can be overridden by subclasses."""
        output.append(self.name, self.value)
