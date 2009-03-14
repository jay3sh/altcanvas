
import sys
from inkface.canvas import ClutterCanvas

try:
    canvas = ClutterCanvas()

    canvas.eventloop()

except KeyboardInterrupt, ki:
    canvas.stop()
