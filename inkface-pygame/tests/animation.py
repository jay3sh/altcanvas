from inkface.canvas import PygameFace, PygameCanvas

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

        self.canvas = PygameCanvas((800,480))
        self.canvas.add(face)
        self.canvas.eventloop()

    def drawPlate(self, elem, screen):
        if self.moveOffset <= 0:

            elem.svg.y -= 3
            self.plateCounter += 1

            if self.plateCounter >= 5:  
                self.moveOffset += 3
                self.plateCounter = 0
            
        screen.blit(elem.sprite.image,(elem.svg.x,elem.svg.y))

    def moveUp(self):
        self.moveOffset += -(self.plates[0].svg.h)



App().main()


