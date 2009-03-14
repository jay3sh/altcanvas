
import sys
from inkface.canvas import ClutterFace, ClutterCanvas

class App:
    def main(self):
        self.canvas = ClutterCanvas((800,480))
        face = ClutterFace(sys.argv[1])

        face.okButton.onLeftClick = self.handleOk
        face.cancelButton.onLeftClick = self.handleCancel

        self.canvas.add(face)
        self.canvas.eventloop()

    def handleOk(self, elem):
        print 'Handling OK'

    def handleCancel(self, elem):
        self.canvas.stop()
        sys.exit(0)


App().main()
