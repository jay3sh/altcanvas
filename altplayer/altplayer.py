#!/usr/bin/env python

import sys
import os

import altplayerlib
from altplayerlib import *
from altplayerlib.coverart import scan_music
from altplayerlib.db import DB,Record,getDB

class Config(Record):
    pass

def main():


    if not os.access(CONFIG_DIR,os.W_OK):
        # This is the first time 
        os.mkdir(CONFIG_DIR)

    if not os.access(COVERART_DIR,os.W_OK):
        os.mkdir(COVERART_DIR)

    db = getDB(altplayerlib.DB_PATH)
    config = db.get(Config())

    if not config:
        if len(sys.argv) < 2:
            print 'Provide path where Music is stored'
            sys.exit(1)
        else:
            config = Config(MUSIC_PATH=sys.argv[1])
            db.put(config)
            path2scan = sys.argv[1]
    else:
        path2scan = config[0].MUSIC_PATH
        
    scan_music(path2scan)


if __name__ == '__main__':
    main()
