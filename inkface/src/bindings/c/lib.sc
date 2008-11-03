#---------------------------------------------------
# SConscript for building native inkface bindings
#---------------------------------------------------

import os

Import('env')

env.AppendUnique(CFLAGS=['-Isrc/lib'])

#
# Library dependencies
#
env.ParseConfig("pkg-config --cflags --libs libaltsvg")

#
# Build the library
#
nativelib = env.SharedLibrary(target='inkface',
                        source=['inkface.c',
                            '#src/lib/common.c'])

if type(nativelib) == type([]): nativelib = nativelib[0]

env.Command('libinkface-native.so','libinkface.so',
            [
                Move("$TARGET","$SOURCE"),
            ])

env.Alias('native-lib',nativelib)

