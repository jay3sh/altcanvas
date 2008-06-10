#!/usr/bin/env python

import sys
import os

from altplayerlib.coverart import scan_music
from altplayerlib.db import DB,Record

class Config(Record):
    pass

def main():

    if len(sys.argv) < 2 or '-?' in sys.argv:
        print "Give me a path"
    else:
        db = DB(os.getenv('HOME')+'/.altplayer.db')
        settings = db.get(Config())
        if not settings:
            db.put(Config(music_store=sys.argv[1]))


        settings = db.get(Config())
        print settings[0].music_store
if __name__ == '__main__':
    main()
