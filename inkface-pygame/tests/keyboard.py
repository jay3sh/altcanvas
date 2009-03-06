

import sys
from inkface.canvas import PygameFace, PygameCanvas


class App:
    FRAMERATE = 5

    def main(self):
        self.canvas = PygameCanvas((800,480))
        self.face = PygameFace(sys.argv[1])


        for i in range(26):
            keyChr = chr(ord('A')+i)
            smlKey = self.face.get('key'+keyChr)
            smlKey.onLeftClick = self.onLeftClick

            self.face.clone('key'+keyChr, 'key'+keyChr+'med')
            self.face.clone('key'+keyChr, 'key'+keyChr+'big')

            medKey = self.face.get('key'+keyChr+'med')
            bigKey = self.face.get('key'+keyChr+'big')

            medKey.svg.scale(1.5)
            bigKey.svg.scale(2)

            medKey.refresh(svg_reload=True)
            bigKey.refresh(svg_reload=True)

            medKey.onDraw = self.doNotDraw
            bigKey.onDraw = self.doNotDraw

            medKey.x = smlKey.x + smlKey.svg.w/2 - medKey.svg.w/2
            bigKey.x = smlKey.x + smlKey.svg.w/2 - bigKey.svg.w/2

            bigKey.y = smlKey.y - 70
            medKey.y = smlKey.y - 30

        self.canvas.add(self.face)
        self.canvas.paint()
        self.canvas.eventloop()

    def doNotDraw(self, elem):
        pass

    def doDraw(self, elem):
        self.canvas.draw(elem)
        elem.onDraw = self.doNotDraw

        if elem.svg.label.endswith('med'):
            bigkeyLabel = elem.svg.label.replace('med','big')
            self.face.get(bigkeyLabel).onDraw = self.doDraw

    def onLeftClick(self, elem):
        medkeyLabel = elem.svg.label+'med'
        self.face.get(medkeyLabel).onDraw = self.doDraw
        self.canvas.animate(self.FRAMERATE,3)

App().main()
