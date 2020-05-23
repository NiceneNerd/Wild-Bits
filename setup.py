# Copyright 2020 Nicene Nerd <macadamiadaze@gmail.com>
# Licensed under GPLv3+

from setuptools import setup
from wildbits.__version__ import VERSION

with open('docs/README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='wildbits',
    version=VERSION,
    author='NiceneNerd',
    author_email='macadamiadaze@gmail.com',
    description='A GUI frontend for Leoetlino\'s Python tools for Breath of the Wild modding',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/NiceneNerd/Wild-Bits/',
    include_package_data = True,
    packages = ['wildbits'],
    entry_points = {
        'gui_scripts': [
            'wildbits = wildbits.__main__:main'
        ]
    },
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.7'
    ],
    python_requires = '>=3.7',
    install_requires = [
        'botw-utils >= 0.2.0',
        'oead >= 1.1.1',
        'rstb',
        'pymsyt >= 0.1.5',
        'xxhash',
        'pywebview >= 3.2, < 4.0',
    ],
    extras_require={"CEF": ["cefpython3~=66.0"]}
)