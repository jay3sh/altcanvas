#!/usr/bin/env python

from distutils.core import setup
import bdist_debian

setup(name='altplayer',
	version='0.1',
	description='Media player based on AltCanvas',
	author='Jayesh Salvi',
	author_email='jayeshsalvi@gmail.com',
	url='http://code.google.com/p/altcanvas/',
	scripts=['altplayer.py'],
    data_files=[
                ('share/applications/hildon',['altplayer.desktop']),
                ],
	packages=['altplayerlib'],
	cmdclass={'bdist_debian': bdist_debian.bdist_debian}
)
