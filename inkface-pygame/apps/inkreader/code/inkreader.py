
#!/usr/bin/env python

import sys
from inkface.canvas import PygameFace, PygameCanvas

SVG_FILE='/home/jayesh/altcanvas/inkface-pygame/apps/inkreader/svg/inkreader.svg'

class App:
    def get_word(self, fd):
        pending_newline = False
        for line in fd:
            words = line.split(' ')
            for word in words:
                if pending_newline:
                    pending_newline = False
                    yield '\n'
                else:
                    if word.find('\n') >= 0:
                        pending_newline = True
                        word = word.replace('\n','')
                    yield word
            
    
    
    def get_line(self, fd):
        curline = ''
        for word in self.get_word(fd):
            if word == '\n':
                yield curline
                curline = ''
            else:
                if not self.length_check(curline, word):
                    yield curline
                    curline = word
                else:
                    curline += ' '+word
            
    def length_check(self, line, word):
        self.line_elem.svg.text = line+' '+word
        self.line_elem.refresh(svg_reload=True)
        return (self.line_elem.svg.w < \
            (self.pad_elem.svg.w - 3*self.margin))
        
    
    def main(self):
        try:
            self.face = PygameFace(SVG_FILE)
        
            canvas = PygameCanvas(
                        (int(float(self.face.svg.width)),
                            int(float(self.face.svg.height))),
                        framerate = 0)
        
            bookname = sys.argv[1]
    
            bookf = open(bookname,'r')
    
            self.face.clone('page','roughpage')
            self.face.roughpage.hide()
    
            self.line_elem = self.face.roughpage
            self.pad_elem = self.face.pad
            self.margin = self.face.page.svg.x
    
            i = 0
            page = ''
            self.line_generator = self.get_line(bookf)
            while True:
                line = self.line_generator.next()
                print line
                page += line+'\n'
                i += 1
                if i > 25:
                    break
    
            self.face.page.svg.text = page
            self.face.page.refresh(svg_reload=True)

            canvas.add(self.face)
            canvas.paint()
            canvas.eventloop()
        
        except Exception, e:
            import traceback
            print traceback.format_exc()
            print 'Caught Exception: '+str(e)
            sys.exit(0)
        
if __name__ == '__main__':
    App().main()
    
