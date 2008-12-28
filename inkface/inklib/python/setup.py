#!/usr/bin/env python

from distutils.core import setup
import bdist_debian

setup(name='inklib',
	version='0.1.0',
	description='Inkface wrapper library',
	author='Jayesh Salvi',
	author_email='jayeshsalvi@gmail.com',
	url='http://code.google.com/p/altcanvas/',
	packages=['inklib'],
    depends='inkface-python (>= 0.1.2)',
	cmdclass={'bdist_debian': bdist_debian.bdist_debian}
)
