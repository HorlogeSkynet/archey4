"""Entry base class"""

from abc import ABC as AbstractBaseClass, abstractmethod

from archey.configuration import Configuration


class Entry(AbstractBaseClass):
    """Module base class"""
    @abstractmethod
    def __init__(self, name=None, value=None, options=None):
        # Each entry will have always have the following attributes...
        # `name`: key;
        # `value`: value of entry as an appropriate object;
        # `options`: configuration options *specific* to an entry instance
        # ... which are `None` by default.
        self.name = name
        self.value = value
        self.entry_options = options or {}

        # Propagates a reference to `Configuration` singleton to each inheriting class.
        self._configuration = Configuration()


    def output(self, output):
        """Output the results to output. Can be overridden by subclasses."""
        if self.value:
            # Let's assume we can just use `__str__` on the object in value,
            # and create a single-line output with it.
            output.append(self.name, str(self.value))
        else:
            # If the value is "falsy" leave a generic "Not detected" message for this entry.
            output.append(
                self.name,
                self._configuration.get('default_strings')['not_detected']
            )
