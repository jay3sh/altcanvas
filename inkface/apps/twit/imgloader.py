
import os
import re
import cairo

import inkface
import inklib
import twitter
from keyboard import Keyboard
import threading
import login

class ImageLoader(threading.Thread):

    stop = False
    __img_map_lock__ = None
    __img_map__ = {}
    IMG_CACHE_DIR = os.environ['HOME']+os.sep+'.twitinkface'

    def __init__(self,urls=None):
        threading.Thread.__init__(self)
        if urls:
            for url in urls:
                localfile = self.IMG_CACHE_DIR+os.sep+'-'.join(url.split('/')[-2:])
                self.__img_map__[url] = localfile
        try:
            os.makedirs(self.IMG_CACHE_DIR)
        except OSError,oe:
            # File already exists
            pass

        self.__img_map_lock__ = threading.Lock()
    
    def get_image_surface(self,url):
        self.__img_map_lock__.acquire()
        localfile = self.__img_map__[url]
        self.__img_map_lock__.release()

        if localfile:
            if not localfile.endswith('png'):
                png_name = '.'.join(localfile.split('.')[:-2]) + '.png'
                if not os.path.exists(png_name):
                    print "PNG file doesn't exist for "+url
                    return None
                else:
                    return cairo.ImageSurface.create_from_png(png_name)
            else:
                return cairo.ImageSurface.create_from_png(localfile)
        else:
            # Image is not yet loaded
            return None

    def add_img_url(self,url):
        self.__img_map_lock__.acquire()
        
        if (type(url) == list or type(url) == tuple):
            print 'Adding %d images to map'%len(url)
            for u in url:
                localfile = self.IMG_CACHE_DIR+os.sep+'-'.join(u.split('/')[-2:])
                self.__img_map__[u] = localfile
        else:
            print 'Adding '+str(url)
            localfile = self.IMG_CACHE_DIR+os.sep+'-'.join(url.split('/')[-2:])
            self.__img_map__[url] = localfile

        self.__img_map_lock__.release()

    def run(self):
        import urllib
        from PIL import Image
        from time import sleep
        while True:
            self.__img_map_lock__.acquire()
            map_items = self.__img_map__.items()
            self.__img_map_lock__.release()

            #print 'IL: Fetching images'
            for url,localfile in map_items:
                if localfile and not os.path.exists(localfile):
                    urllib.urlretrieve(url,localfile)
                    if not localfile.endswith('png'):
                        jpg = Image.open(localfile)
                        png_name = '.'.join(localfile.split('.')[:-2]) + '.png'
                        jpg.save(png_name)

                    if self.stop:
                        return

            #print 'IL: sleeping for 2 sec'
            sleep(2)
            
            if self.stop:
                return
         
