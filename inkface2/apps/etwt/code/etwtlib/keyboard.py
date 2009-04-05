
from inkface.evas import EFace

class Keyboard:
    def __init__(self, svgname, canvas):
        self.face = EFace(svgname, canvas)

        self._capsLockOff()

        self.face.key_Caps.onLeftClick = self.onCapsLock

    def hide(self):
        for e in self.face.elements:
            e.hide()

    def unhide(self):
        #for e in self.face.elements:
        #    e.unhide()
        if self._capsLock:
            self._capsLockOn()
        else:
            self._capsLockOff()

    def onCapsLock(self, elem):
        self._capsLockOn()

    def _capsLockOn(self):
        for e in self.face.elements:
            if e.svg is not None and e.svg.label is not None and \
                e.svg.label[3].islower():
                e.hide()
            else:
                e.unhide()

        self.face.key_Caps.hide()
        self._capsLock = True

    def _capsLockOff(self):
        for e in self.face.elements:
            if e.svg is not None and e.svg.label is not None and \
                e.svg.label[3].isupper():
                print 'hiding '+e.svg.label
                e.hide()
            else:
                print 'unhiding '+e.svg.label
                e.unhide()
        self.face.key_Caps.unhide()
        self._capsLock = False
