
import os

Import('env')

#
# Library dependencies
#
env.ParseConfig("pkg-config --cflags --libs libaltsvg")

env.AppendUnique(CFLAGS=['-g'])
env.AppendUnique(CFLAGS=['-Isrc/lib'])
env.AppendUnique(CFLAGS=['-DDOUBLE_BUFFER'])

nativelib = env.SharedLibrary(target='inkface',
                        source=['inkface.c',
                            '#src/lib/common.c'])

if type(nativelib) == type([]): nativelib = nativelib[0]

env.Command('libinkface-native.so','libinkface.so',
            [
                Move("$TARGET","$SOURCE"),
            ])

env.Alias('native-lib',nativelib)


