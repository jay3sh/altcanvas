
import os
import urllib
import gtk.gdk
import threading
from time import sleep

from etwtlib.constants import *

IMG_WIDTH   = 32
IMG_HEIGHT  = 32

class ImageThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
        if not os.path.exists(IMAGE_CACHE_DIR):
            os.makedirs(IMAGE_CACHE_DIR)

        self.image_map = {}

        self.work_queue = []

        self.stop_flag = False

    def add_work(self, work):
        self.work_queue.append(work)

    def stop(self):
        self.stop_flag = True

    def run(self):
        while True:
            if self.stop_flag: return

            if len(self.work_queue) == 0:
                sleep(2)
                continue


            url, elem = self.work_queue[0]

            path = self.download_image(url)
            if path is None:
                print url
            else:
                elem.refresh(svg_reload=False, imgpath=path)

            del self.work_queue[0]

    def download_image(self, url):

        if self.image_map.has_key(url):
            return self.image_map[url]

        localfile = os.path.join(IMAGE_CACHE_DIR,url.split('/')[-1])
        
        if not os.path.exists(localfile):
            try:
                urllib.urlretrieve(url, localfile)
            except UnicodeError, ue:
                print 'Error fetching img URL'+str(ue)
                return None 
            except IOError, ioe:
                print 'IOError fetching img: '+str(ioe)
                return None
        
        pixbuf = gtk.gdk.pixbuf_new_from_file(localfile)
        basename = localfile.rpartition('.')[0]
        pngfile = basename + '.png'

        pixbuf.scale_simple(IMG_WIDTH, IMG_HEIGHT, gtk.gdk.INTERP_NEAREST)
        pixbuf.save(pngfile, "png")        

        return pngfile
