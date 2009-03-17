#!/usr/bin/python

import sys
import getopt


template_python_app = \
'''
#!/usr/bin/env python

import sys
from inkface.canvas import PygameFace, PygameCanvas

def main():
    try:
        face = PygameFace(sys.argv[1])
    
        canvas = PygameCanvas(
                    (int(float(face.svg.width)),
                        int(float(face.svg.height))),
                    framerate = 0)
    
        canvas.add(face)
        canvas.paint()
        canvas.eventloop()
    
    except Exception, e:
        print 'Caught Exception: '+str(e)
        sys.exit(0)
    
if __name__ == '__main__':
    main()

'''

template_setup_py = \
'''
#!/usr/bin/env python

from distutils.core import setup
import os

setup(name='%s',
    version='0.0.1',
    description='SVG GUI Framework Inkface with pygame backend',
    author='XXX',
    author_email='XXX@XXX.com',
    url='XXX',
    scripts=['%s'],
    data_files=[],
    packages=['%s']
)
'''

def generate_project(destdir, projname, binname, libname):
    import os
    SEP = os.path.sep

    if destdir is None:
        usage()
        return

    if projname is None:
        usage()
        return

    if binname is None:
        binname = projname

    if libname is None:
        libname = binname+'lib'


    os.makedirs(os.path.join(destdir,projname,'svg'))
    os.makedirs(os.path.join(destdir,projname,'code'))

    # write a template .svg file under svg

    # write a template .py file under code
    binfile = open(os.path.join(destdir,projname,'code',binname),'w')
    binfile.write(template_python_app)
    binfile.close()

    os.makedirs(os.path.join(destdir,projname,'code',libname))

    # write a setup.py
    setupfile = open(os.path.join(destdir,projname,'code','setup.py'),'w')
    setupfile.write(template_setup_py%(projname,binname,libname))
    setupfile.close()

def usage():
    print 'Inkface App generation script:'
    print ' appgen.py [options]'
    print ' '
    print ' -d --dir        : destination directory to generate project files'
    print ' -p --projname   : Name of project (a subdir under destination '
    print '                   directory is created with this name'
    print ' -b --binname    : Name of program file (as in /usr/bin/<binname>'
    print ' -l --libname    : Name of library (as in '
    print '                   /usr/lib/python-<ver>/site-packages/<libname>'
    print ' -h --help       : usage'

def main():
    args = sys.argv[1:]

    try:
        optlist, args = getopt.getopt(args,'hd:p:b:l:',
                        ['help','dir=','projname=','binname=','libname='])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(0)
    
    destdir = None
    projname = None
    binname = None
    libname = None
    for o,a in optlist:
        if o in ('-h','--help'):
            usage()
            return
        elif o in ('-d','--dir'):
            destdir = a
        elif o in ('-p','--projname'):
            projname = a
        elif o in ('-b', '--binname'):
            binname = a
        elif o in ('-l', '--libname'):
            libname = a
            
            
    generate_project(destdir, projname, binname, libname)

if __name__ == '__main__':
    main()
