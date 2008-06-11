#!/usr/bin/env python

import sys
import os

from altplayerlib.coverart import scan_music
from altplayerlib.db import DB,Record

class Config(Record):
    pass

def main():

    db = DB(os.getenv('HOME')+'/.altplayer.db')
    settings = db.get(Config())
    if not settings:
        if len(sys.argv) < 2:
            print "Give me a path"
            sys.exit(0)
        else:
            db.put(Config(music_store=sys.argv[1]))

    settings = db.get(Config())
    scan_music(settings[0].music_store)



if __name__ == '__main__':
    main()
