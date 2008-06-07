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

def normalize(string):
    string = string.lower().strip()
    string = string.replace('unknown','')
    string = string.replace(' ','%20')
    return string

def main():
    amazon = Amazon()

    if len(sys.argv) < 2 or '-?' in sys.argv:
        print "Give me a path"
    else:
        success_count = 0
        total_count = 0
        for root,dir,files in os.walk(sys.argv[1]):
            for mp3 in files:
                try:
                    print mp3
                    if not mp3.lower().endswith('mp3'):
                        continue 

                    total_count += 1

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
                    print 'Tags: %s-%s-%s-%s-%s-%s'%(
                        album,performer,title,tt2,tpe1,talb)

                    for tag in (album,performer,title):
                        if tag:
                            keywords.append(normalize(tag))

                    if len(keywords) == 0:
                        songname = mp3.lower().rpartition('.')[0]
                        songinfo = songname.split('-')
                        for part in songinfo:
                            keywords.append(normalize(part))

                    if len(keywords) == 0:
                        for tag in (tt2,tpe1,talb):
                            if tag:
                                keywords.append(normalize(tag))

                    keywords = unique(keywords)
                    keywords = filter_trivial_kw(keywords)

                    print 'Flat: '+str(keywords)

                    while len(keywords) > 0:
                        results = amazon.search(keywords)

                        # If search fails try with fewer keywords
                        if not results or len(results) <= 0:
                            keywords = keywords[:-1]
                            continue

                        images = amazon.getImages(results[0])

                        # If getImage fails try with fewer keywords
                        if not images:
                            keywords = keywords[:-1]
                            continue

                        success_count += 1
                        print 'Success: '+str(keywords)
                        print " "*10+" --> "+images[0]
                        break

                except Exception, e:
                    for line in traceback.format_exc().split('\n'):
                        print line
    
        print 'Success ratio: %d/%d'%(success_count,total_count)

if __name__ == '__main__':
    main()
