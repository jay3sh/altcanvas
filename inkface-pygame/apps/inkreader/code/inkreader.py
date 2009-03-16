
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
            (self.pad_elem.svg.w - 2*self.margin))
        
    
    def main(self):
        try:
            self.face = PygameFace(SVG_FILE)
        
            self.canvas = PygameCanvas(
                        (int(float(self.face.svg.width)),
                            int(float(self.face.svg.height))),
                        framerate = 0)
        
            bookname = sys.argv[1]

            title = bookname.rpartition('/')[-1]
            title = title.rpartition('.')[-3]

            self.face.title.svg.text = title
            self.face.title.refresh(svg_reload=True)
    
            bookf = open(bookname,'r')
    
            self.face.clone('page','roughpage')
            self.face.roughpage.hide()
    
            self.line_elem = self.face.roughpage
            self.pad_elem = self.face.pad
            self.margin = self.face.page.svg.x

            self.face.downArrow.onLeftClick = self.moveDown
            self.face.upArrow.onLeftClick = self.moveUp

            self.num_lines = \
                (self.face.pad.svg.h-self.face.page.svg.y) \
                /(1.3*self.face.page.svg.h)

            i = 0
            self.page_lines = []
            self.line_generator = self.get_line(bookf)
            while True:
                line = self.line_generator.next()
                self.page_lines.append(line)
                i += 1
                if i > self.num_lines:
                    break
    
            print len(self.page_lines)
            self.face.page.svg.text = '\n'.join(self.page_lines)
            self.face.page.refresh(svg_reload=True)

            self.canvas.add(self.face)
            self.canvas.paint()
            self.canvas.eventloop()
        
        except Exception, e:
            import traceback
            print traceback.format_exc()
            print 'Caught Exception: '+str(e)
            sys.exit(0)
        
    def moveUp(self, elem):
        pass

    def moveDown(self, elem):
        self.page_lines = self.page_lines[1:]
        self.page_lines.append(self.line_generator.next())

        self.face.page.svg.text = '\n'.join(self.page_lines)
        self.face.page.refresh(svg_reload=True)

        self.canvas.paint()

if __name__ == '__main__':
    App().main()
    
