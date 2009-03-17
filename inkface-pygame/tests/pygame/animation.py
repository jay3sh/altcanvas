

import sys
import os
import pygame
from inkface.canvas.pygamecanvas import PygameFace, PygameCanvas

class gbl:
    FRAMERATE = 12

class App:
    plateCounter = 0
    moveOffset = 0
    def main(self):
        face = PygameFace(sys.argv[1])

        if os.environ.get('INKFACE_FULLSCREEN') is not None:
            flags = pygame.FULLSCREEN
        else:
            flags = 0
 
        self.plates = (face.onePlate, 
                    face.twoPlate, 
                    face.threePlate, 
                    face.fourPlate, 
                    face.fivePlate)

        for plate in self.plates:
            plate.onDraw = self.drawPlate

        if gbl.FRAMERATE > 0:
            face.upArrow.onLeftClick = self.moveUp
            face.downArrow.onLeftClick = self.moveDown

        self.moveStep = self.plates[0].svg.h
        self.moveDir = 0

        self.canvas = PygameCanvas(
            (int(face.svg.width),int(face.svg.height)),
            framerate=gbl.FRAMERATE,
            flags = flags)

        self.canvas.add(face)

        try:
            self.canvas.eventloop()
        except KeyboardInterrupt, ki:
            sys.exit(0)

    def drawPlate(self, elem):
        if self.moveDir != 0:
            elem_x, elem_y = elem.get_position()
            elem_y += self.moveDir * int(self.moveStep/gbl.FRAMERATE)
            elem.set_position((elem_x,elem_y))
            self.plateCounter += 1

            if self.plateCounter >= 5:  
                self.plateCounter = 0

                self.moveAmount -= int(self.moveStep/gbl.FRAMERATE)
                if self.moveAmount < int(self.moveStep/gbl.FRAMERATE):
                    self.moveDir = 0
                    self.moveAmount = 0


    def moveUp(self, elem):
        self.moveDir += -1
        self.moveAmount = self.moveStep
        self.canvas.update()

    def moveDown(self, elem):
        self.moveDir += +1
        self.moveAmount = self.moveStep
        self.canvas.update()


#import cProfile
#cProfile.run('App().main()','animation.txt')
App().main()

