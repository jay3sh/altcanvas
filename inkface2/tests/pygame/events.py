
import sys
import os
import pygame
from inkface.canvas.pygamecanvas import PygameFace, PygameCanvas

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

        self.face.okButton.onLeftClick = self.handleOk
        self.face.cancelButton.onLeftClick = self.handleCancel
        self.canvas.add(self.face)
        self.canvas.paint()
        self.canvas.eventloop()

    def handleOk(self, elem):
        print 'Handling OK'

    def handleCancel(self, elem):
        self.canvas.stop()
        sys.exit(0)


#import cProfile
#cProfile.run('App().main()','events-numpy.txt')
App().main()






