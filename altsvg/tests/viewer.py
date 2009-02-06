
import gtk
import altsvg

def draw(cr):
    cr.set_source_rgb(1,1,0)
    cr.move_to(1,1)
    cr.line_to(10,10)
    cr.stroke()

class ViewingArea(gtk.DrawingArea):
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.connect("expose-event",self.do_expose)
        self.connect("key-press-event",self.do_expose)

    def do_expose(self,event,data):
        cr = self.window.cairo_create()
        draw(cr)

class ViewWindow(gtk.Window):
    def __init__(self,width,height):
        gtk.Window.__init__(self)
        self.resize(width,height)

def main():
    window = ViewWindow(300,300)
    window.connect("destroy", gtk.main_quit)
    window.show()

    widget = ViewingArea()
    window.add(widget)
    widget.show()

    gtk.main()

def main2():
    import altsvg
    altsvg.SVGParser('data/basic.svg')

if __name__ == '__main__':
    main2()
