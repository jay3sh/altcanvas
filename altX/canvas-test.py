
import sys
sys.path.append('/home/jayesh/trunk/altcanvas/altX/.libs')


from time import sleep
import cairo
import canvasX


surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,10,10)
ctx = cairo.Context(surface)
ctx.set_source_rgba(1,1,1,0.5)
ctx.rectangle(2,2,8,8)
ctx.fill()

if not surface:
    print 'surface creation failed'

canvasX.run()

for i in range(1,200):
    canvasX.draw(surface,10+i,10+i)
    sleep(0.1)

canvasX.close()


