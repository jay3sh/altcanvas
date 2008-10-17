#!/usr/bin/python
import sys
import pygst
pygst.require("0.10")
import gst
import gtk
gtk.threads_init()
import threading
import inkface

player = None
filename = '/media/mmc2/music/sia-breathe-me.mp3'

def play(e,elist):
    global player
    player.play(filename)
    
def main():
    global canvas

    elements = inkface.loadsvg(sys.argv[1])
    fullscreen = False
    try:
        if os.environ['INKFACE_FULLSCREEN']:
            fullscreen = True
    except:
        pass
    canvas = inkface.canvas(fullscreen=fullscreen)
    canvas.register_elements(elements)

    for el in elements:
        if el.name == 'playButton':
            el.onMouseEnter = play

    # app logic
    global player
    player = Player()
    player.start()

    # eventloop
    canvas.show()
    canvas.eventloop()
 
class Player(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.create_pipeline()
    
    def create_pipeline(self):
        # Create GStreamer bits and bobs
 
        self.pipeline = gst.Pipeline("mypipeline")
 
        self.audiosrc = gst.element_factory_make("gnomevfssrc","source")
        self.pipeline.add(self.audiosrc)
 
        self.audiosink = gst.element_factory_make("dspmp3sink", "sink")
        self.pipeline.add(self.audiosink)
 
        self.audiosrc.link(self.audiosink)
 
    def run(self):
        gtk.main()

    def play(self, file_name):
        gtk.threads_enter()
        self.audiosrc.set_property("location", file_name)       
        self.pipeline.set_state(gst.STATE_READY) 
        self.pipeline.set_state(gst.STATE_PLAYING)
        gtk.threads_leave()
 
    def pause(self, widget):
        self.pipeline.set_state(gst.STATE_PAUSED)
 
    def stop(self, widget):
        if self.pipeline.get_state() != gst.STATE_PAUSED:
            self.pipeline.set_state(gst.STATE_PAUSED)
        if self.pipeline.get_state() != gst.STATE_NULL:
            self.pipeline.set_state(gst.STATE_NULL)
 

main()
