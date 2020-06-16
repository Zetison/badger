#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='badger',
    version='0.1.0',
    description='A batch runner tool',
    author='Eivind Fonn',
    author_email='eivind.fonn@sintef.no',
    license='AGPL3',
    url='https://github.com/TheBB/Badger',
    packages=['badger'],
    entry_points={
        'console_scripts': ['badger=badger.__main__:main'],
    },
)
