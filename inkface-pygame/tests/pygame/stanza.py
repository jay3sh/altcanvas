import sys
from inkface.canvas import PygameFace, PygameCanvas

try:
    face = PygameFace(sys.argv[1])

    stanza_text = '''
        Blow, blow, thou winter wind
        Thou art not so unkind
        As man's ingratitude;
        Thy tooth is not so keen,
        Because thou art not seen,
        Although thy breath be rude
            -- William Shakespeare
        '''

    face.stanza.svg.text = stanza_text
    face.stanza.refresh(svg_reload=True)
    canvas = PygameCanvas(
        (int(float(face.svg.width)),int(float(face.svg.height))),
        framerate=0)

    canvas.add(face)

    canvas.paint()

    canvas.eventloop()
except KeyboardInterrupt, ki:
    sys.exit(0)
