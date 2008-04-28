import sys
sys.path.append('/home/jayesh/workspace/altcanvas/altX/.libs')

import altX 
import cairo
from time import sleep

surface = altX.AltXSurface()

ctx = cairo.Context(surface)

ctx.set_source_rgba(1,1,1,1)

ctx.rectangle(10,10,20,20)

ctx.fill()

surface.flush()

sleep(5)

