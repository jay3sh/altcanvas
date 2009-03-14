
import sys
from inkface.canvas import ClutterFace, ClutterCanvas

class App:
    def main(self):
        
        self.canvas = ClutterCanvas((800,480))
        self.face = ClutterFace(sys.argv[1])

        self.face.changeButton.onLeftClick = self.change

        self.canvas.add(self.face)

        self.canvas.eventloop()

    def change(self, elem):

        self.face.changeText.svg.text = 'This is new text!'
        self.face.changeText.refresh()

App().main()
