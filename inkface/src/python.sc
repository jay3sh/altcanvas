env = Environment()


######
# libinface-python.so
######
import distutils.sysconfig, os
vars = distutils.sysconfig.get_config_vars('CC', 'CXX', 'OPT', \
                        'BASECFLAGS', 'CCSHARED', 'LDSHARED', 'SO')
for i in range(len(vars)):
    if vars[i] is None:
        vars[i] = ""
(cc, cxx, opt, basecflags, ccshared, ldshared, so_ext) = vars

env.ParseConfig("pkg-config --cflags --libs libaltsvg")

env.AppendUnique(CPPPATH=[distutils.sysconfig.get_python_inc()])

env.AppendUnique(CPPFLAGS=[basecflags + " " + opt])

lib = env.SharedLibrary(target='inkface-python',
                source=['inkface-python.c'])

if type(lib) == type([]): lib = lib[0]

env.Command('inkface.so','libinkface-python.so',
            [
                Move("$TARGET","$SOURCE"),
            ])
