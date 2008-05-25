
import sys
sys.path.append('/home/jayesh/trunk/altcanvas/altX/.libs')
sys.path.append('/home/jayesh/trunk/altcanvas/common')
import canvasX


from time import sleep
import cairo

from libpub.prime.app import PublishrApp

class Canvas:
    def __init__(self):
        canvasX.create()

    def key_handler(self,key):
        pass

    def motion_notify(self,x,y):
        print '%d,%d'%(x,y)

    def load(self):
        self.app = PublishrApp()

    def run(self):
        canvasX.run()

    def redraw(self):
        pass

    def redraw_i(self):
        self.app.redraw()
        canvasX.draw(self.app.surface,0,0)

    def unload(self):
        canvasX.close()

if __name__ == '__main__':
    canvas = Canvas()
    import libpub
    libpub.prime.canvas = canvas

    canvas.load()
    canvas.redraw_i()

    canvas.run()
    canvas.unload()


