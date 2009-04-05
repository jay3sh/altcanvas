
from inkface.evas import EFace

class Keyboard:
    def __init__(self, svgname, canvas):
        self.event_map = {}

        self.face = EFace(svgname, canvas)

        self._capsLockOff()

        self.face.key_Caps.onLeftClick = self.onCapsLock

        self.face.key_Enter.onLeftClick = self.onEnter


    def connect(self, event_str, callback):
        if not self.event_map.has_key(event_str):
            self.event_map[event_str] = []

        self.event_map[event_str].append(callback)

    def emit(self, event_str):
        if not self.event_map.has_key(event_str):
            return

        for handler in self.event_map[event_str]:
            handler()
        

    def onEnter(self, elem):
        self.emit('done')

    def hide(self):
        for e in self.face.elements:
            e.hide()

    def unhide(self):
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
                e.hide()
            else:
                e.unhide()
        self.face.key_Caps.unhide()
        self._capsLock = False
