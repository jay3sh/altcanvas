#!/usr/bin/env python

import sys
import os

from altplayerlib.coverart import scan_music

def main():

    if len(sys.argv) < 2 or '-?' in sys.argv:
        print "Give me a path"
    else:
        scan_music(sys.argv[1])

if __name__ == '__main__':
    main()
