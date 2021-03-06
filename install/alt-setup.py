#!/usr/bin/env python

from distutils.core import setup
import bdist_debian

setup(name='altpublishr-maemo',
	version='0.6.1',
	description='Photo publishing to Flickr/Picasa from Maemo device',
	author='Jayesh Salvi',
	author_email='jayesh@altfrequency.com',
	url='http://code.google.com/p/altcanvas/',
	scripts=['altpublishr.py',],
    data_files=[
                ('share/applications/hildon',['altpublishr.desktop']),
                ('share/altpublishr/icons',['altpublishr.png','note.png','globe.png'])
                ],
	packages=['libpub', 'libpub.utils', 'libpub.prime', 'libpub.prime.widgets','libpub.gdata','libpub.gdata.base','libpub.gdata.photos','libpub.gdata.geo','libpub.gdata.media','libpub.gdata.exif','libpub.atom'],
	cmdclass={'bdist_debian': bdist_debian.bdist_debian}
)
