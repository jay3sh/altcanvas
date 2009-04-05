
import sys
from inkface.clutter import ClutterFace, ClutterCanvas

canvas = ClutterCanvas((800,480))

face = ClutterFace(sys.argv[1])

canvas.add(face)

canvas.eventloop()

