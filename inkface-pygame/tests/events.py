
from inkface.canvas import PygameFace, PygameCanvas

class App:
    def main(self):
        self.canvas = PygameCanvas((800,480))
        face = PygameFace('data/gui-0.svg')
        face.okButton.onLeftClick = self.handleOk
        face.cancelButton.onLeftClick = self.handleCancel
        self.canvas.add(face)
        self.canvas.paint()
        self.canvas.eventloop()

    def handleOk(self):
        print 'Handling OK'

    def handleCancel(self):
        print 'Handling Cancel'


App().main()






