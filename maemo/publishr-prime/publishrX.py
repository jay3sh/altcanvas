
import sys
sys.path.append('/home/jayesh/trunk/altcanvas/altX/.libs')
sys.path.append('/home/jayesh/trunk/altcanvas/common')
import canvasX


from time import sleep
import cairo

from libpub.prime.app import PublishrApp

class Canvas:
    isLoaded = False

    def __init__(self):
        canvasX.create()

    def key_handler(self,key):
        pass

    def motion_handler(self,x,y):
        if self.isLoaded:
            self.app.dispatch_pointer_event(x,y,True)

    def load(self):
        self.app = PublishrApp()
        canvasX.register_motion_handler(self)
        self.isLoaded = True

    def run(self):
        canvasX.run()

    def redraw(self):
        if self.isLoaded:
            self.app.redraw()
            canvasX.draw(self.app.surface,0,0)

    def unload(self):
        canvasX.close()
        sys.exit(0)

if __name__ == '__main__':
    canvas = Canvas()
    import libpub
    libpub.prime.canvas = canvas

    canvas.load()
    canvas.redraw()

    canvas.run()
    canvas.unload()


