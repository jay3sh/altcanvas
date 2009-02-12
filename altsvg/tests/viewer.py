#
# This file is part of altcanvas.
#
# altcanvas - SVG based GUI framework
# Copyright (C) 2009  Jayesh Salvi <jayeshsalvi@gmail.com>
#
# Distributed under GNU General Public License version 3
#

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
    cr.set_source_rgb(1,0,0)

    cr.rel_move_to(20,20)
    cr.rel_line_to(width,0)
    cr.rel_line_to(0,height)
    cr.rel_line_to(-width,0)
    cr.rel_line_to(0,-height)

    cr.stroke_preserve()

    cr.set_source_rgb(1,1,0)

    #cr.fill()

    cr.clip()

    cr.paint_with_alpha(0.25)
    
    cr.restore()

    #cr.rel_move_to(0,0)
    #cr.rel_line_to(200,10)
    #cr.stroke()
    
class App:
    vectorDoc = None
    def __init__(self):
        pass

    def do_expose(self,event,data):
        cr = self.widget.window.cairo_create()

        #drawexp(cr)
        self.vectorDoc.render_full(cr)

    def main(self):
        self.vectorDoc = altsvg.VectorDoc('data/basic.svg')
        w,h = self.vectorDoc.get_doc_props()
        window = ViewWindow(int(w),int(h))
    
        window.connect("destroy", gtk.main_quit)
        window.show()
    
        self.widget = ViewingArea(self.do_expose)

        window.add(self.widget)
        self.widget.show()

        gtk.main()

if __name__ == '__main__':
    App().main()
