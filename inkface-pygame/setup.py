#!/usr/bin/env python

from distutils.core import setup
import os

try:
    files = os.listdir('tests/data')
    svg_list = filter(lambda x: x.endswith('.svg'), files)
    svg_list = map(lambda x: 'tests/data/'+x, svg_list)
    
    files = os.listdir('tests')
    test_list = filter(lambda x: x.endswith('.py'), files)
    test_list = map(lambda x: 'tests/'+x, test_list)
except Exception,e:
    test_list = []
    svg_list = []
    
setup(name='inkface-pygame',
    version='0.2.0',
    description='SVG GUI Framework Inkface with pygame backend',
    author='Jayesh Salvi',
    author_email='jayeshsalvi@gmail.com',
    url='http://code.google.com/p/altcanvas',
    scripts=[],
    data_files=[
                ('share/applications/inkface-pygame/tests/',test_list),
                ('share/applications/inkface-pygame/tests/data',svg_list),
                ],
    packages=['inkface','inkface.altsvg','inkface.canvas']
)
