from inkface.canvas import PygameFace, PygameCanvas

class gbl:
    FRAMERATE = 15

class App:
    plateCounter = 0
    moveOffset = 0
    def main(self):
        face = PygameFace('data/gui-1.svg')

        self.plates = (face.onePlate, 
                    face.twoPlate, 
                    face.threePlate, 
                    face.fourPlate, 
                    face.fivePlate)

        for plate in self.plates:
            plate.onDraw = self.drawPlate

        face.upArrow.onLeftClick = self.moveUp
        face.downArrow.onLeftClick = self.moveDown

        self.moveStep = self.plates[0].svg.h
        self.moveDir = 0

        self.canvas = PygameCanvas((800,480),framerate=15)
        self.canvas.add(face)
        self.canvas.eventloop()

    def drawPlate(self, elem, screen):
        if self.moveDir != 0:

            elem.svg.y += self.moveDir * int(self.moveStep/gbl.FRAMERATE)
            self.plateCounter += 1

            if self.plateCounter >= 5:  
                self.plateCounter = 0

                self.moveAmount -= int(self.moveStep/gbl.FRAMERATE)
                if self.moveAmount < int(self.moveStep/gbl.FRAMERATE):
                    self.moveDir = 0
                    self.moveAmount = 0
            
        screen.blit(elem.sprite.image,(elem.svg.x,elem.svg.y))

    def moveUp(self):
        self.moveDir += -1
        self.moveAmount = self.moveStep

    def moveDown(self):
        self.moveDir += +1
        self.moveAmount = self.moveStep


App().main()


