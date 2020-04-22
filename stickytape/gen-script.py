"""Helper script to generate a single-file standalone Archey script using stickytape."""

from glob import iglob
from subprocess import call

# build a list of `archey.entries` modules to tell stickytape to import
archey_entry_imports = ['archey.entries']
for path in iglob('archey/entries/*.py'):
    if not path.split('/')[-1].startswith('_'):
        archey_entry_imports.append(
            'archey.entries.{0}'.format(path.split('/')[-1][:-3])
        )

# create arguments for stickytape
arguments = [
    '--add-python-path', '.',
    '--output-file', 'dist/archey'
]
for entry in archey_entry_imports:
    arguments.extend(['--add-python-module', entry])

arguments.append('archey/__main__.py')

# use call instead of run for Python <3.5 compatibility
# (return value of this process doesn't really matter since output is to stdout & stderr)
call(['stickytape'] + arguments)
