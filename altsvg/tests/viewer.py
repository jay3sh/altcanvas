
import gtk
import altsvg

class ViewingArea(gtk.DrawingArea):
    def __init__(self,expose_handler):
        gtk.DrawingArea.__init__(self)
        self.connect("expose-event",expose_handler)


class ViewWindow(gtk.Window):
    def __init__(self,width,height):
        gtk.Window.__init__(self)
        self.resize(width,height)

def drawexp(cr):
    #cr.move_to(10,10)
    #cr.line_to(200,200)
    #cr.stroke()

    cr.move_to(200,200)

    cr.set_source_rgb(1,0,0)

    cr.save()
    
    width = 60
    height = 60
    cr.set_source_rgb(1,1,0)
    cr.rel_move_to(20,20)
    cr.rel_line_to(width,0)
    cr.rel_line_to(0,height)
    cr.rel_line_to(-width,0)
    cr.rel_line_to(0,-height)
    cr.stroke()
    
    cr.restore()

    cr.rel_move_to(0,0)
    cr.rel_line_to(200,10)
    cr.stroke()


    
class App:
    tree = None
    def __init__(self):
        pass

    def do_expose(self,event,data):
        cr = self.widget.window.cairo_create()

        #drawexp(cr)
        altsvg.render_full(cr,self.tree)

    def main(self):
        self.tree = altsvg.load('data/basic.svg')
        w,h = altsvg.extract_doc_data(self.tree)
        window = ViewWindow(int(w),int(h))
    
        window.connect("destroy", gtk.main_quit)
        window.show()
    
        self.widget = ViewingArea(self.do_expose)

        window.add(self.widget)
        self.widget.show()

        gtk.main()

if __name__ == '__main__':
    App().main()
