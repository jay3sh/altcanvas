
import sys

from PyQt4 import QtGui, QtCore
from inkface.altsvg import VectorDoc

class App(QtGui.QMainWindow):
    def __init__(self, svgname):
        QtGui.QMainWindow.__init__(self)

        self.scene = QtGui.QGraphicsScene()

        self.view = QtGui.QGraphicsView(self.scene)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.view.setInteractive(True)
        self.setCentralWidget(self.view)

        self.vDoc = VectorDoc(svgname)

        self.resize(int(self.vDoc.width), int(self.vDoc.height))

        


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    window = App(sys.argv[1])
    window.show()

    sys.exit(app.exec_())
