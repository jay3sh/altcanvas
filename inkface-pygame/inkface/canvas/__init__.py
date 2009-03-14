'''Canvas Backend module of inkface'''
    
from canvas import Face, Canvas, CanvasElement
try:
    from pygamecanvas import \
        PygameFace, PygameCanvas, PygameCanvasElement
except ImportError, ie:
    print "Warning: Pygame backend won't be supported"
    print ie

try:
    from cluttercanvas import \
        ClutterFace, ClutterCanvas, ClutterCanvasElement
except ImportError, ie:
    print "Warning: Clutter backend won't be supported"
    print ie
