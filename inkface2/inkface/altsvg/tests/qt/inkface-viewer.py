
import sys

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QPoint
from inkface.altsvg import VectorDoc

class App(QtGui.QMainWindow):
    def __init__(self, svgname):
        QtGui.QMainWindow.__init__(self)

        self.vDoc = VectorDoc(svgname)
        #self.resize(int(self.vDoc.width), int(self.vDoc.height))

        self.scene = QtGui.QGraphicsScene(0,0,
            self.vDoc.width, self.vDoc.height)

        self.view = QtGui.QGraphicsView(self.scene)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.view.setInteractive(True)
        self.setCentralWidget(self.view)


        elements = self.vDoc.get_qt_elements()
        
        for e in elements:
            prect = self.scene.addPixmap(e.pixmap)
            prect.setPos(self.view.mapToScene(QPoint(e.x, e.y)))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    window = App(sys.argv[1])
    window.show()

    sys.exit(app.exec_())
