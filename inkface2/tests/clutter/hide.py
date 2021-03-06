
import sys
from inkface.clutter import ClutterFace, ClutterCanvas

class App:
    def main(self):
        self.canvas = ClutterCanvas((800,480))
        self.face = ClutterFace(sys.argv[1])
        self.face.hideButton.onLeftClick = self.handleHide
        self.face.unhideButton.onLeftClick = self.handleUnhide
        self.canvas.add(self.face)
        try:
            self.canvas.eventloop()
        except KeyboardInterrupt, ki:
            self.canvas.stop()
            sys.exit(0)
 
    def handleHide(self, elem):
        self.face.theobj.hide()

    def handleUnhide(self, elem):
        self.face.theobj.unhide()

App().main()
