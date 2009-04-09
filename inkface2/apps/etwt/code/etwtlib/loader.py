
import os

from inkface.evas import EFace, ECanvas
from etwtlib.inkobject import InkObject

from etwtlib.constants import *
import evas
import math

class Loader(InkObject):
    def __init__(self):
        InkObject.__init__(self)

    def load(self):
        self.face = EFace(os.path.join(SVG_DIR,'default','loader.svg'))

        self.canvas = ECanvas(
                            (int(float(self.face.svg.width)),
                            int(float(self.face.svg.height))),
                            framerate = FRAMERATE)

        self.face.load_elements(self.canvas)

        self.face.meterBullet.onDraw = self.drawMeter

        self.first_draw = True

        self.X_MIN = self.face.svg.width/7
        self.X_MAX = 6*self.face.svg.width/7 - self.face.meterBullet.svg.w

        return self.canvas

    def drawMeter(self, elem):
        x, y = elem.get_position()

        x += 5

        if x >= self.X_MAX:
            x = self.X_MIN

        elem.set_position((x, y))

        return True
