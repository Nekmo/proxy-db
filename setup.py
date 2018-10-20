#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

PACKAGE = 'proxy_db'

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    # TODO: put package requirements here
]

setup_requirements = [
    'pytest-runner',
    # TODO(Nekmo): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

package_version = __import__(PACKAGE).__version__


setup(
    name='proxy-db',
    version=package_version,
    description="Manage free and private proxies on local db for Python Projects.",
    long_description=readme + '\n\n' + history,
    author="Nekmo Com",
    author_email='contacto@nekmo.com',
    url='https://github.com/Nekmo/proxy-db',
    packages=find_packages(include=['proxy_db']),
    entry_points={
        'console_scripts': [
            'proxy_db=proxy_db.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='proxy_db',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
