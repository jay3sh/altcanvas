import sys

from PyQt4 import QtGui, QtCore


class App(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.scene = QtGui.QGraphicsScene()

        self.view = QtGui.QGraphicsView(self.scene)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.view.setInteractive(True)
        self.setCentralWidget(self.view)

        pixmap = QtGui.QPixmap(50,50)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter()
        painter.begin(pixmap)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255,255,255)))
        painter.drawLine(10,10,20,20)
        painter.end()

        image = self.scene.addPixmap(pixmap)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    window = App()

    window.show()

    sys.exit(app.exec_())
