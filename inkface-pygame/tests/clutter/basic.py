
import sys
from inkface.canvas import ClutterFace, ClutterCanvas

try:
    canvas = ClutterCanvas((800,480))

    face = ClutterFace(sys.argv[1])

    canvas.add(face)

    canvas.eventloop()

except KeyboardInterrupt, ki:
    print 'caught ki'
    canvas.stop()
