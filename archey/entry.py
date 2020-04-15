"""Entry base class"""

from archey.configuration import Configuration

class Entry():
    """Module base class"""
    def __init__(self):
        # Default to naming the class as its `display_text` config option.
        self.name = Configuration()["entries"][type(self).__name__]["display_text"]
        self.value = None

    def output(self, output):
        """Output the results to output. Can be overridden by subclasses."""
        output.append(self.name, self.value)
