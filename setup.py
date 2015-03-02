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
    'skosprovider>=0.4.0',
    'requests>=1.0.0'
]

setup(
    name='skosprovider_oe',
    version='0.4.1',
    description='A SKOS provider for OE vocabularies.',
    long_description=open('README.rst').read() + '\n\n' +
                     open('HISTORY.rst').read(),
    author='Koen Van Daele',
    author_email='koen_van_daele@telenet.be',
    url='http://github.com/koenedaele/skosprovider_oe',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'skosprovider_oe': 'skosprovider_oe'},
    include_package_data=True,
    install_requires = requires,
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
)
