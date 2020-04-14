"""Module base class"""


class Module():
    """Module base class"""

    def output(self, output):
        """Output the results to output. Can be overridden by subclasses."""
        output.append(self.name, self.value)
