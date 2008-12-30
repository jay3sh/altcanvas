#!/usr/bin/env python

from distutils.core import setup
import bdist_debian

setup(name='twitter-inkface',
	version='0.1.0',
	description='Twitter client with Inkface GUI',
	author='Jayesh Salvi',
	author_email='jayeshsalvi@gmail.com',
	url='http://code.google.com/p/altcanvas/',
	packages=['twitink'],
	scripts=['twit.py'],
    data_files=[
                ('share/applications/hildon',['twitink.desktop']),
                ('share/pixmaps/twitink/keyboard.svg',['keyboard.svg']),
                ('share/pixmaps/twitink/login.svg',['login.svg']),
                ('share/pixmaps/twitink/public.svg',['public.svg']),
                ],
    depends='inkface-python (>= 0.1.2), inklib (>= 0.1.0)',
	cmdclass={'bdist_debian': bdist_debian.bdist_debian}
)
