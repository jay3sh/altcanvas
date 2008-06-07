#!/usr/bin/env python

import sys
import os
import traceback

from altplayerlib.id3reader import Reader as id3Reader
from altplayerlib.utils import unique
from altplayerlib.coverart import Amazon

COVERART_DIR='/tmp/coverart'

trivial_keywords = ('to','of','the')

def filter_trivial_kw(kw):
    for tkw in trivial_keywords:
        if tkw in kw:
            kw.remove(tkw)

    return kw

def main():
    amazon = Amazon()

    if len(sys.argv) < 2 or '-?' in sys.argv:
        print "Give me a path"
    else:
        for root,dir,files in os.walk(sys.argv[1]):
            for mp3 in files:
                try:
                    id3 = id3Reader(os.path.join(root,mp3))

                    tt2,tpe1,talb,performer,album,title = ( 
                        id3.getValue('TIT2'),
                        id3.getValue('TPE1'),
                        id3.getValue('TALB'),
                        id3.getValue('performer'),
                        id3.getValue('album'),
                        id3.getValue('title')
                    )

                    keywords = []
                    for tag in (album,performer,title,tt2,tpe1,talb):
                        if tag:
                            keywords += tag.lower().split()

                    keywords = unique(keywords)
                    keywords = filter_trivial_kw(keywords)

                    if len(keywords) > 0:
                        results = amazon.search(keywords)
                        if not results or len(results) <= 0:
                            #print 'No results found: '+str(keywords)
                            continue

                        images = amazon.getImages(results[0])

                        if not images:
                            #print 'No images found: '+results[0]
                            continue

                        print mp3+"\n"+" "*10+" --> "+images[0]

                except Exception, e:
                    for line in traceback.format_exc().split('\n'):
                        print line
    

if __name__ == '__main__':
    main()
