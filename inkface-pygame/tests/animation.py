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

        if gbl.FRAMERATE > 0:
            face.upArrow.onLeftClick = self.moveUp
            face.downArrow.onLeftClick = self.moveDown

        self.moveStep = self.plates[0].svg.h
        self.moveDir = 0

        self.canvas = PygameCanvas((800,480),framerate=gbl.FRAMERATE)
        self.canvas.add(face)

        self.canvas.paint()

        self.canvas.eventloop()

    def drawPlate(self, elem):
        if self.moveDir != 0:

            elem.y += self.moveDir * int(self.moveStep/gbl.FRAMERATE)
            self.plateCounter += 1

            if self.plateCounter >= 5:  
                self.plateCounter = 0

                self.moveAmount -= int(self.moveStep/gbl.FRAMERATE)
                if self.moveAmount < int(self.moveStep/gbl.FRAMERATE):
                    self.moveDir = 0
                    self.moveAmount = 0
            
        self.canvas.draw(elem)

    def moveUp(self):
        self.moveDir += -1
        self.moveAmount = self.moveStep
        self.canvas.animate(gbl.FRAMERATE,gbl.FRAMERATE)

    def moveDown(self):
        self.moveDir += +1
        self.moveAmount = self.moveStep
        self.canvas.animate(gbl.FRAMERATE,gbl.FRAMERATE)


App().main()


