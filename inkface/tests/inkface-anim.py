
#!/usr/bin/env python

import re
import sys
import inkface

canvas = None
ANIM_SVG=sys.argv[1]


def onFrameDraw(e):
    global canvas
    m = re.match('\w+frame(\d+)',e.name)
    if m and int(m.group(1)) == frame_count:
        canvas.draw(e)


def main():
    global canvas
    elements = inkface.loadsvg(ANIM_SVG)
    canvas = inkface.canvas()
    canvas.register_elements(elements)

    for e in elements:
        if re.match('\w+frame(\d+)',e.name):
            e.onDraw = onFrameDraw
            
    canvas.set_timer(1000)
    canvas.show()
    canvas.eventloop()

if __name__ == '__main__':
    main()
