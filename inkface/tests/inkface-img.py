#!/usr/bin/python

import inkface
import inklib
import cairo
from PIL import Image

class MainFace(inklib.Face):
    def __init__(self,canvas,svgname):
        inklib.Face.__init__(self,canvas,svgname)
        assert(self.imgFrame)

        jpg = Image.open('data/batman.jpg')
        jpg.save('/tmp/batman.png')
        imgSurface = cairo.ImageSurface.create_from_png('/tmp/batman.png')

        imgCtx = cairo.Context(self.imgFrame.surface)
        imgCtx.set_source_surface(imgSurface,0,0)
        imgCtx.paint()


def main():
    canvas = inkface.create_X_canvas()
    canvas.add(MainFace(canvas,'data/img.svg'))

    canvas.eventloop()

if __name__ == '__main__':
    main()
