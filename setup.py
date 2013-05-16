#!/usr/bin/env python

import os

import skosprovider_oe

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'skosprovider_oe',
]

requires = [
    'skosprovider>=0.2.0',
    'requests>=1.0.0'
]

setup(
    name='skosprovider_oe',
    version='0.2.0',
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
    install_requires = requires,
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2'
    ],
)
