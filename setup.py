#!/usr/bin/env python

import os
import sys

import skosprovider_oe

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

packages = [
    'skosprovider_oe',
]

requires = [
    'skosprovider',
    'requests>0.14,<0.14.99'
]

setup(
    name='skosprovider_oe',
    version='0.1.0',
    description='A SKOS provider for OE vocabularies.',
    long_description=open('README.rst').read() + '\n\n' +
                     open('HISTORY.rst').read(),
    author='Koen Van Daele',
    author_email='koen_van_daele@telenet.be',
    url='http://github.com/koenedaele/skosprovider_oe',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'skosprovider': 'skosprovider'},
    include_package_data=True,
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)

del os.environ['PYTHONDONTWRITEBYTECODE']
