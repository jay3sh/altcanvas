
import gtk
import altsvg

def draw(cr):
    cr.set_source_rgb(1,1,0)
    cr.move_to(1,1)
    cr.line_to(10,10)
    cr.stroke()

class ViewingArea(gtk.DrawingArea):
    def __init__(self,expose_handler):
        gtk.DrawingArea.__init__(self)
        self.connect("expose-event",expose_handler)


class ViewWindow(gtk.Window):
    def __init__(self,width,height):
        gtk.Window.__init__(self)
        self.resize(width,height)

class App:
    tree = None
    def __init__(self):
        pass

    def do_expose(self,event,data):
        cr = self.widget.window.cairo_create()

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
