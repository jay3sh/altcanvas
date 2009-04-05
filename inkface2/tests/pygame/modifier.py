
import sys
import os
import pygame
from inkface.pygame import PygameFace, PygameCanvas

class App:
    def main(self):
        self.face = PygameFace(sys.argv[1])
        if os.environ.get('INKFACE_FULLSCREEN') is not None:
            flags = pygame.FULLSCREEN
        else:
            flags = 0
        self.canvas = PygameCanvas(
            (int(self.face.svg.width),int(self.face.svg.height)),
            flags = flags,
            framerate = 0)

        self.face.resizeButton.onLeftClick = self.handleResize
        self.canvas.add(self.face)
        self.canvas.paint()
        self.canvas.eventloop()

    def handleResize(self, elem):
        self.face.rectObj.svg.set('width','500')
        self.face.rectObj.refresh(svg_reload=True)
        self.canvas.paint()



App().main()






