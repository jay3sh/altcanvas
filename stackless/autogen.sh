#!/bin/sh

set -e
set -x

rm -rf *.cache *.m4 config.guess config.log \
config.status config.sub depcomp ltmain.sh

(cat aclocal/*.m4 > acinclude.m4 2> /dev/null)

autoreconf --verbose --install --symlink

