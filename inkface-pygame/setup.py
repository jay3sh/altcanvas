#!/usr/bin/env python

from distutils.core import setup
import os

setup(name='inkface-pygame',
    version='0.2.0',
    description='SVG GUI Framework Inkface with pygame backend',
    author='Jayesh Salvi',
    author_email='jayeshsalvi@gmail.com',
    url='http://code.google.com/p/altcanvas',
    scripts=[],
    data_files=[],
    packages=['inkface','inkface.altsvg','inkface.canvas']
)
