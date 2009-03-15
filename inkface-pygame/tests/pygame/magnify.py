#!/usr/bin/python


import sys
import os
import pygame
from inkface.canvas import PygameFace, PygameCanvas

class App:
    def main(self):
        face = PygameFace(sys.argv[1])

        if os.environ.get('INKFACE_FULLSCREEN') is not None:
            flags = pygame.FULLSCREEN
        else:
            flags = 0
 
        self.canvas = PygameCanvas(
            (int(face.svg.width),int(face.svg.height)),
            flags = flags)

        face.xelem.svg.scale(2)
        face.xelem.refresh(svg_reload=True)

        self.canvas.add(face)

        self.canvas.paint()

        self.canvas.eventloop()



App().main()



