#!/usr/bin/env python

import sys
import os

def scan():
    import altplayerlib
    from altplayerlib import *
    from altplayerlib.coverart import scan_music
    from altplayerlib.db import DB,Record,getDB

    class Config(Record):
        pass

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
        

def main():
    import canvasX
    import cairo
    from time import sleep
    import altplayerlib
    from altplayerlib.song import CoverartRecord
    from altplayerlib.db import DB,Record,getDB
    
    canvasX.create()

    db = getDB(altplayerlib.DB_PATH)
    songs = db.get(CoverartRecord())

    def get_thumbnail_png_surface(path):
        png_path = path + '.thumb.png'
        im = Image.open(path)
        im.thumbnail((100,100),Image.ANTIALIAS)
        im.save(png_path)
        return cairo.ImageSurface.create_from_png(png_path)
        
    background = cairo.ImageSurface(cairo.FORMAT_ARGB32,800,480)
    bctx = cairo.Context(background)
    bctx.set_source_rgba(1,1,1,0.25)
    bctx.rectangle(0,0,800,480)
    bctx.fill()

    i = 0
    for song in songs:
        from PIL import Image
        if song.IMAGE_PATH:
            surface = get_thumbnail_png_surface(song.IMAGE_PATH)

        bctx.set_source_surface(surface,10+i*5,10+i*3)
        bctx.paint()
        canvasX.draw(background,0,0)
        i+=1

    sleep(5)

    canvasX.close()

    sys.exit(0)

if __name__ == '__main__':
    import getopt
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hs:", 
                        ["help","scan="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if not opts:
        main()
        sys.exit()

    for o,a in opts:
        if o in ("-h","--help"):
            usage()
            sys.exit()
        if o in ("-s","--scan"):
            scan_music(a)
            sys.exit()

        main()
