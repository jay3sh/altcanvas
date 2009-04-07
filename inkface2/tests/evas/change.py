import sys
from inkface.evas import ECanvas, EFace

class App:
    def main(self):
        try:
            self.face = EFace(sys.argv[1])
        
            canvas = ECanvas((self.face.svg.width,self.face.svg.height))
        
            self.face.load_elements(canvas)
        
            self.face.changeButton.onLeftClick = self.change
        
            canvas.eventloop()
        except KeyboardInterrupt, ki:
            sys.exit(0)
    
    def change(self, elem):
        self.face.changeText.svg.text = 'This is new text!'
        self.face.changeText.refresh()
        
App().main()
