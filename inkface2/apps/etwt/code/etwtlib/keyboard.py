
from inkface.evas import EFace

class Keyboard:
    def __init__(self, svgname, canvas):
        self.event_map = {}

        self.face = EFace(svgname, canvas)

        self._capsLockOff()

        self.face.key_Caps.onLeftClick = self.onCapsLock

        self.face.key_Enter.onLeftClick = self.onEnter

        for e in self.face.elements:
            if e.svg.label[3] != '_':
                e.onLeftClick = self.onKeyClick


    def connect(self, event_str, callback):
        if not self.event_map.has_key(event_str):
            self.event_map[event_str] = []

        self.event_map[event_str].append(callback)

    def disconnect(self, event_str, callback):
        if not self.event_map.has_key(event_str) or \
            self.event_map[event_str] is None:
            return
        self.event_map[event_str].remove(callback)

    def emit(self, event_str, *args):
        if not self.event_map.has_key(event_str) or \
            self.event_map[event_str] is None:
            return

        for handler in self.event_map[event_str]:
            handler(*args)

    def onKeyClick(self, elem):
        assert elem.svg is not None and elem.svg.label is not None
        keyVal = elem.svg.label[3]
        self.emit('keypress',keyVal)

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
