
#!/usr/bin/env python

import sys
from inkface.canvas import PygameFace, PygameCanvas

SVG_FILE='/home/jayesh/altcanvas/inkface-pygame/apps/inkreader/svg/inkreader.svg'

def main():
    try:
        face = PygameFace(SVG_FILE)
    
        canvas = PygameCanvas(
                    (int(float(face.svg.width)),
                        int(float(face.svg.height))),
                    framerate = 0)
    
        bookname = sys.argv[1]

        bookf = open(bookname,'r')

        MAX_LEN = 50 
        txtlines = []
        i = 0
        for line in bookf:
            while len(line) > 0:
                if len(line) < MAX_LEN:
                    txtlines.append(line)
                    line = ''
                else:
                    txtlines.append(line[:MAX_LEN])
                    line = line[MAX_LEN:]

                if len(txtlines) > 20:
                    break
                
            if len(txtlines) > 20:
                break

        face.textobj.svg.text = '\n'.join(txtlines)
        face.textobj.refresh(svg_reload=True)

        canvas.add(face)
        canvas.paint()
        canvas.eventloop()
    
    except Exception, e:
        import traceback
        print traceback.format_exc()
        print 'Caught Exception: '+str(e)
        sys.exit(0)
    
if __name__ == '__main__':
    main()

