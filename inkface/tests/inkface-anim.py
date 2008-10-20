
#!/usr/bin/env python

import re
import sys
import inkface

canvas = None
frame_count = 0
ANIM_SVG=sys.argv[1]


def onFrameDraw(e):
    global canvas
    global frame_count

    m = re.match('\w+frame(\d+)',e.name)

    if m and int(m.group(1)) == (frame_count+1):
        print e.name
        canvas.draw(e)

def onTimer():
    global frame_count
    print 'onTimer %d'%(frame_count)
    frame_count += 1
    frame_count %= 3


def main():
    global canvas
    elements = inkface.loadsvg(ANIM_SVG)
    canvas = inkface.canvas()
    canvas.register_elements(elements)

    for e in elements:
        if re.match('\w+frame(\d+)',e.name):
            e.onDraw = onFrameDraw
            
    canvas.set_timer(1000,onTimer)
    canvas.show()
    canvas.eventloop()

if __name__ == '__main__':
    main()
