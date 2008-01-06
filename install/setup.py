#!/usr/bin/env python

from distutils.core import setup
import bdist_debian

setup(name='publishr-maemo',
	version='0.4',
	description='Photo publishing to Flickr/Picasa from Maemo device',
	author='Jayesh Salvi',
	author_email='jayeshsalvi@gmail.com',
	url='http://code.google.com/p/altcanvas/',
	scripts=['publishr.py','publishr-start.py'],
    data_files=[
                ('share/applications/hildon',['publishr.desktop']),
                ],
	packages=['libpub', 'libpub.utils', 'libpub.gdata', 'libpub.gdata.base', 'libpub.gdata.photos', 'libpub.gdata.geo', 'libpub.gdata.media', 'libpub.gdata.exif', 'libpub.atom' ],
	cmdclass={'bdist_debian': bdist_debian.bdist_debian}
)
