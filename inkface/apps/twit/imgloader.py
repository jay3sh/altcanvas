
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
        try:
            localfile = self.__img_map__[url]
        except KeyError, ke:
            self.__img_map_lock__.release()
            return None
        self.__img_map_lock__.release()

        if localfile:
            if not localfile.endswith('png'):
                png_name = '.'.join(localfile.split('.')[:-1]) + '.png'
                if not os.path.exists(png_name):
                    #print "PNG file doesn't exist for "+url
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
            for u in url:
                localfile = self.IMG_CACHE_DIR+os.sep+'-'.join(u.split('/')[-2:])
                self.__img_map__[u] = localfile
        else:
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

            for url,localfile in map_items:
                if localfile:
                    if not os.path.exists(localfile):
                        try:
                            urllib.urlretrieve(url,localfile)
                        except UnicodeError, ue:
                            print 'Error fetching img URL'+str(ue)
                            continue

                    if not localfile.endswith('png'):
                        try:
                            jpg = Image.open(localfile)
                            png_name = \
                                '.'.join(localfile.split('.')[:-1]) + '.png'
                            jpg.save(png_name)
                        except IOError,ioe:
                            # We cannot process this image
                            self.__img_map_lock__.acquire()
                            del self.__img_map__[url]
                            self.__img_map_lock__.release()
                            print 'Error processing '+localfile+': '+str(ioe)

                    if self.stop:
                        return

            sleep(2)
            
            if self.stop:
                return
         
