
import sys
from inkface.canvas import PygameFace, PygameCanvas

class App:
    def main(self):
        self.canvas = PygameCanvas((800,480))
        face = PygameFace(sys.argv[1])
        face.okButton.onLeftClick = self.handleOk
        face.cancelButton.onLeftClick = self.handleCancel
        self.canvas.add(face)
        self.canvas.paint()
        self.canvas.eventloop()

    def handleOk(self, elem):
        print 'Handling OK'

    def handleCancel(self, elem):
        self.canvas.stop()
        sys.exit(0)


#import cProfile
#cProfile.run('App().main()','events-numpy.txt')
App().main()






