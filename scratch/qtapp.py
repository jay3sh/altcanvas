import sys

from PyQt4 import QtGui, QtCore


class Canvas(QtGui.QWidget):
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawLine(10,10,20,20)

class App(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        canvas = Canvas()

        self.setCentralWidget(canvas)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    window = App()

    window.show()

    sys.exit(app.exec_())
