#!/usr/bin/env python3

"""
This is the Archey 4's `setup.py` file, allowing us to distribute it as a package...
... with cool meta-data.
"""

import os

from setuptools import find_packages, setup

from archey._version import __version__


setup(
    name='archey4',
    version=__version__.lstrip('v'),
    description='Archey is a simple system information tool written in Python',
    keywords='archey python3 linux system-information monitoring screenshot',
    url='https://github.com/HorlogeSkynet/archey4',
    author='Samuel Forestier',  # Not alone
    author_email='dev+archey@samuel.domains',
    license='GPLv3',
    packages=find_packages(exclude=['archey.test*']),
    test_suite='archey.test',
    python_requires='>=3.5',
    install_requires=[
        'distro',
        'netifaces'
    ],
    entry_points={
        'console_scripts': [
            'archey = archey.__main__:main'
        ]
    },
    long_description="""\
Archey4 is a **maintained** fork of the original Archey Linux system tool.
The original Archey program had been written by Melik Manukyan in 2009, and quickly abandoned in 2011.
At first, it only supported Arch Linux distribution, further support had been added afterwards.
Many forks popped in the wild due to inactivity, but this one attends since 2017 to succeed where the others failed:
Remain *maintained*, *community-driven* and *highly-compatible* with yesterday's and today's systems.\
""",
    long_description_content_type='text/x-rst',
    data_files=[
        # By filtering on `os.path.exists`, install should succeed even when
        #   the compressed manual page is not available (iterable would be empty).
        ('share/man/man1', filter(os.path.exists, ['dist/archey.1.gz'])),
        ('share/doc/archey4', ['README.md', 'COPYRIGHT.md'])
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: System'
    ]
)
