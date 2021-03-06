#---------------------------------------------------
# SConscript for building python inkface bindings
#---------------------------------------------------

Import('env')

env.AppendUnique(CFLAGS=['-Isrc/lib'])

env.AppendUnique(CFLAGS=['-pg'])

env.AppendUnique(LINKFLAGS="-pg")
#
# Resolve generic library dependencies using pkg-config
#
env.ParseConfig("pkg-config --cflags --libs xext")
env.ParseConfig("pkg-config --cflags --libs pycairo")

Import('ARCH')
#if ARCH != 'armel':
#    env.ParseConfig("pkg-config --cflags --libs gl")
#    #env.AppendUnique(LINKFLAGS="-lglut")
#    env.AppendUnique(CFLAGS=['-DHAS_OPENGL'])

#
# Resolve python dependencies using distutils
#
import distutils.sysconfig, os
vars = distutils.sysconfig.get_config_vars('CC', 'CXX', 'OPT', \
                        'BASECFLAGS', 'CCSHARED', 'LDSHARED', 'SO')
for i in range(len(vars)):
    if vars[i] is None:
        vars[i] = ""
(cc, cxx, opt, basecflags, ccshared, ldshared, so_ext) = vars
env.AppendUnique(CPPPATH=[distutils.sysconfig.get_python_inc()])

#
# Build the library
#
pythonlib = env.SharedLibrary(target='inkface',
                source=['inkface.c',
                        'canvas.c', 
                        'element.c',
                        '#src/lib/common.c', 
                        '#src/lib/canvas-x.c',
                        '#src/lib/canvas-gl.c'])

if type(pythonlib) == type([]): pythonlib = pythonlib[0]

inkface_module = env.Command('inkface.so','libinkface.so',
            [
                Move("$TARGET","$SOURCE"),
            ])

env.Alias('python-lib','inkface.so')

Import('PREFIX')
env.Install(dir = PREFIX+distutils.sysconfig.get_python_lib(), source=inkface_module)

env.Alias('install', PREFIX+distutils.sysconfig.get_python_lib())
