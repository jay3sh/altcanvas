import glob
from py2deb import Py2deb

AUTHOR  = "Jayesh Salvi"
MAIL    = "jayeshsalvi@gmail.com"
VERSION = "0.2.5"
BLDVERSION  = "0"
URL     = "http://code.google.com/p/altcanvas"
LICENSE = "gpl"
SECTION = "user/system"
ARCH    = "all"

def fill_common_details(p):
    p.author        = AUTHOR
    p.mail          = MAIL
    p.url           = URL
    p.license       = LICENSE
    p.section       = SECTION
    p.arch          = ARCH


# Inkface core
p = Py2deb("inkface-core")

fill_common_details(p)

p.description   = "SVG based GUI framework library"
lib_files = glob.glob('inkface/*.py')
lib_files += glob.glob('inkface/altsvg/*.py')
p["/usr/lib/python2.5/site-packages"] = lib_files
p.generate(VERSION,BLDVERSION,tar=True,dsc=True,changes=True,build=True,src=True)


# Inkface pygame

p = Py2deb("inkface-pygame")

fill_common_details(p)

p.depends       = "python2.5-cairo, python2.5-pygame, python2.5-xml"
p.description   = "Pygame backend for Inkface"

lib_files = glob.glob('inkface/pygame/*.py')
p["/usr/lib/python2.5/site-packages"] = lib_files
p.generate(VERSION,BLDVERSION,tar=True,dsc=True,changes=True,build=True,src=True)


# Inkface evas

p = Py2deb("inkface-evas")

fill_common_details(p)

p.depends       = "python2.5-evas, python2.5-ecore"
p.description   = "Evas backend for Inkface"

lib_files = glob.glob('inkface/evas/*.py')
p["/usr/lib/python2.5/site-packages"] = lib_files
p.generate(VERSION,BLDVERSION,tar=True,dsc=True,changes=True,build=True,src=True)

