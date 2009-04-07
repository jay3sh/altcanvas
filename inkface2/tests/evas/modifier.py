import sys
from inkface.evas import ECanvas, EFace

class App:
    def main(self):
        try:
            self.face = EFace(sys.argv[1])
        
            canvas = ECanvas((self.face.svg.width,self.face.svg.height))
        
            self.face.load_elements(canvas)
        
            self.face.resizeButton.onLeftClick = self.handleResize
        
            canvas.eventloop()
        except KeyboardInterrupt, ki:
            sys.exit(0)
    
    def handleResize(self, elem):
        self.face.rectObj.svg.set('width', '500')
        self.face.rectObj.refresh()
        
App().main()
