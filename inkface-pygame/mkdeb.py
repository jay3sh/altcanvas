import glob
from py2deb import Py2deb

version="0.2.2"

p = Py2deb("inkface")

p.author = "Jayesh Salvi"
p.mail =  "jayeshsalvi@gmail.com"
p.description = "SVG based GUI framework library"
p.url = "http://code.google.com/p/altcanvas"
p.depends = "python2.5-cairo, python2.5-pygame, python2.5-xml"
p.license="gpl"
p.section="utils"
p.arch="all"


lib_files = glob.glob('inkface/*.py')
lib_files += glob.glob('inkface/altsvg/*.py')
lib_files += glob.glob('inkface/canvas/*.py')
p["/usr/lib/python2.5/site-packages"] = lib_files

p.generate(version,src=True)
