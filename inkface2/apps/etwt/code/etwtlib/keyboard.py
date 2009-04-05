
from inkface.evas import EFace

class Keyboard:
    def __init__(self, svgname, canvas):
        self.face = EFace(svgname, canvas)

    def hide(self):
        for e in self.face.elements:
            e.hide()

    def unhide(self):
        for e in self.face.elements:
            e.unhide()


