
import sys
sys.path.append('/home/jayesh/trunk/altcanvas/altX/.libs')


from time import sleep
import cairo
import canvasX

def key_handler(key):
    pass

def motion_notify(x,y):
    print '%d,%d'%(x,y)

def pressure_handler(x,y,pressure):
    print '%d,%d,%d'%(x,y,pressure)

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,10,10)
ctx = cairo.Context(surface)
ctx.set_source_rgba(1,1,1,0.5)
ctx.rectangle(2,2,8,8)
ctx.fill()

if not surface:
    print 'surface creation failed'

canvasX.create()

canvasX.register_motion_handler(motion_notify)
canvasX.register_pressure_handler(pressure_handler)

'''
for i in range(1,200):
    canvasX.draw(surface,10+i,10+i)
    sleep(0.1)
'''

canvasX.run()

canvasX.close()


