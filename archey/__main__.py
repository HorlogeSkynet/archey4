#!/usr/bin/env python3

"""
Archey main file.
It loads each entry as a different class coming from the `entries` module.
Logos are stored under the `logos` module.
"""

from importlib import import_module

from archey.output import Output
from archey.configuration import Configuration
from archey.processes import Processes

def main():
    """Simple entry point"""

    # Since Processes is a singleton, populate it.
    Processes()

    # Load the configuration.
    configuration = Configuration()

    # Create an output object so entries can be attached to it.
    output = Output()

    # Iterate over the keys of the entries configuration object
    # i.e. the names of the entries to load.
    for entry_key in configuration['entries']:
        # Get an object for the entry and attach it to the output object.
        entry_module = import_module('archey.entries.' + entry_key.lower())
        entry_class = getattr(entry_module, entry_key)
        entry_instance = entry_class()
        output.attach(entry_instance)

    output.output()


if __name__ == '__main__':
    main()
