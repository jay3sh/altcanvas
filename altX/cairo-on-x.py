


import sys
sys.path.append('/home/maemo/sb-maemo/altcanvas/altX/.libs')

import altX
import cairo
from time import sleep

surface = altX.AltXSurface()

ctx = cairo.Context(surface)


grad = cairo.LinearGradient(10,10,10,20)
grad.add_color_stop_rgba(1,1,1,0,1)
grad.add_color_stop_rgba(0,1,0,0,1)
rect = ctx.rectangle(10,10,20,20)
ctx.set_source(grad)

ctx.fill()

sleep(5)
surface.flush()
surface.close()
