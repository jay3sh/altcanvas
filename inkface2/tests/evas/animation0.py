import sys
from inkface.evas import ECanvas, EFace

class App:
    def main(self):
        try:
            self.face = EFace(sys.argv[1])
        
            canvas = ECanvas((self.face.svg.width,self.face.svg.height))
        
            self.face.load_elements(canvas)
        
            self.plates = (self.face.onePlate, 
                    self.face.twoPlate, 
                    self.face.threePlate, 
                    self.face.fourPlate, 
                    self.face.fivePlate)

            #for plate in self.plates:
            #    plate.move_length = 0

            self.face.upArrow.onLeftClick = self.moveUp
            self.face.downArrow.onLeftClick = self.moveDown
       
            self.move_period = 10
            self.move_step = self.face.onePlate.svg.h/self.move_period

            canvas.eventloop()
        except KeyboardInterrupt, ki:
            sys.exit(0)
    
    def drawPlate(self, elem):
        x, y = elem.get_position()

        if elem.move_length <= self.move_step:
            elem.set_position((x, y+self.direction*elem.move_length))
            self.move_length = 0
            return False
        else:
            elem.set_position((x, y+self.direction*self.move_step))
            elem.move_length -= self.move_step
            return True
        
    def moveUp(self, elem):
        self.direction = -1
        for plate in self.plates:
            plate.move_length = plate.svg.h
            plate.onDraw = self.drawPlate

    def moveDown(self, elem):
        self.direction = 1
        for plate in self.plates:
            plate.move_length = plate.svg.h
            plate.onDraw = self.drawPlate
        
App().main()
