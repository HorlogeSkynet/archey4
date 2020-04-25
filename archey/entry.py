"""Entry base class"""

class Entry():
    """Module base class"""
    def __init__(self):
        # Initialise with None values as a starting point
        self.name = None
        self.value = None

    def output(self, output):
        """Output the results to output. Can be overridden by subclasses."""
        output.append(self.name, self.value)
