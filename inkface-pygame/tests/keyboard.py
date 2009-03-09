

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

            medKey.hide()
            bigKey.hide()

            smlKey_x,smlKey_y = smlKey.get_position()
            medKey_x,medKey_y = medKey.get_position()
            bigKey_x,bigKey_y = bigKey.get_position()

            medKey_x = smlKey_x + smlKey.svg.w/2 - medKey.svg.w/2
            medKey_y = smlKey_y - 30
            medKey.set_position((medKey_x,medKey_y))

            bigKey_x = smlKey_x + smlKey.svg.w/2 - bigKey.svg.w/2
            bigKey_y = smlKey_y - 70
            bigKey.set_position((bigKey_x,bigKey_y))


        self.canvas.add(self.face)
        self.canvas.eventloop()

    def doDraw(self, elem):
        if elem.visibility_counter > 0:
            elem.visibility_counter -= 1
        else:
            elem.hide()
            elem.onDraw = None

            if elem.svg.label.endswith('med'):
                bigkeyLabel = elem.svg.label.replace('med','big')
                bigKey = self.face.get(bigkeyLabel)
                bigKey.onDraw = self.doDraw
                bigKey.unhide()
                bigKey.visibility_counter = 2

    def onLeftClick(self, elem):
        medkeyLabel = elem.svg.label+'med'
        medKey = self.face.get(medkeyLabel)
        medKey.onDraw = self.doDraw
        medKey.unhide()
        medKey.visibility_counter = 2

App().main()
