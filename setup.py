
from setuptools import setup


setup(
    name='archey4',
    version='4.4.0',
    description='Archey is a simple system information tool written in Python',
    keywords='archey python3 linux system-information monitoring',
    url='http://git.io/archey4',
    author='Samuel FORESTIER',  # Not alone
    author_email='dev@samuel.domains',
    license='GPLv3',
    packages=['archey'],
    test_suite='test',
    entry_points={
        'console_scripts': [
            'archey = archey.archey:main'
        ]
    },
    long_description='Maintained fork of the original Archey Linux system tool'
                     ' written by Melik Manukyan.',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System'
    ]
)
