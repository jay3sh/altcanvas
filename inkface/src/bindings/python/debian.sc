#------------------------------------------------------------
# Build a debian package for native inkface library bindings
#------------------------------------------------------------

import os

Import('env')
Import('VERSION ARCH MAINTAINER')
DEPENDS = 'libaltsvg (>= 0.1.2)'
DESCRIPTION = 'UI framework based on SVG'

PKGNAME = 'inkface-python'
PKGFILE = '#%s_%s_%s.deb'%(PKGNAME,VERSION,ARCH)

# Get Subversion number to embed in package information
# This may be as simple as '89' or as complex as '4123:4184M'.
# We'll just use the last bit.
svn_version = os.popen('svnversion ..').read()[:-1]
svn_version = svn_version.split(':')[-1]

DEBFILES = [
    ("usr/lib/python2.5/site-packages/inkface.so", 
                                        "#src/bindings/python/inkface.so"),
]

PKGDIR = 'tmpdeb'

DEBCONTROLFILE = os.path.join(PKGDIR, "DEBIAN/control")

for f in DEBFILES:
    dest = os.path.join(PKGDIR,f[0])
    src = f[1]
    env.Depends(PKGFILE,dest)
    env.Command(dest,src,Copy('$TARGET','$SOURCE'))
    env.Depends(DEBCONTROLFILE, dest)

CONTROL_TEMPLATE = """
Package: %s
Priority: extra
Section: misc
Installed-Size: %s
Maintainer: %s
Architecture: %s
Version: %s-%s
Depends: %s
Description: %s
"""
env.Depends(PKGFILE,DEBCONTROLFILE)

# This function creates the control file from the template and info
# specified above, and works out the final size of the package.
def make_control(target, source, env):
    installed_size = 0
    for i in DEBFILES:
        installed_size += os.stat(str(env.File(i[1])))[6]
        control_info = CONTROL_TEMPLATE % (
            PKGNAME, installed_size, MAINTAINER, ARCH, VERSION,
            svn_version, DEPENDS, DESCRIPTION)
        f = open(str(target[0]), 'w')
        f.write(control_info)
        f.close()

env.Command(DEBCONTROLFILE, None, make_control)

def make_debpkg(target,source,env):
    pkgfilename = target[0]
    pkgdir = source[0]
    print os.popen("dpkg-deb -b %s %s"%(pkgdir,pkgfilename)).read()

env.Command(PKGFILE,PKGDIR,make_debpkg)

env.Alias('python-debian',PKGFILE)




