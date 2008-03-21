#!/usr/bin/python
import gtk
from gtk import keysyms
import cairo
import math


def cairo_test(pixmap,w,h):
    ctx = pixmap.cairo_create()
    white_background(ctx,w,h)
    
    gradSurface = lingrad_surface(w-100,h-100)
    
    #surface = solid_surface(w-100,h-100)
    #surface = image_surface('data/test3.png',w-100,h-100)
    surface = text_surface('Hello Cairo!',w-100,h-100)
    
    ctx.set_source_surface(surface,50,50)
    ctx.mask_surface(gradSurface)
    #ctx.paint()
    
def solid_surface(w,h):
    solidSurface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
    ctx = cairo.Context(solidSurface)
    ctx.set_source_rgba(0,1,0,0.5)
    rect = ctx.rectangle(0,0,w,h)
    ctx.fill()
    return solidSurface
    
def lingrad_surface(w,h):
    lingradSurface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
    ctx = cairo.Context(lingradSurface)
    lingrad = cairo.LinearGradient(0.0,0.0,w,h)
    lingrad.add_color_stop_rgba(1,0,0,0,1)
    lingrad.add_color_stop_rgba(0,0,0,0,0)
    rect = ctx.rectangle(0,0,w,h)
    ctx.set_source(lingrad)
    ctx.fill()
    return lingradSurface

def image_surface(path,w,h):
    imageSurface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
    ctx = cairo.Context(imageSurface)
    ctx2 = gtk.gdk.CairoContext(ctx)
    pixbuf = gtk.gdk.pixbuf_new_from_file(path)
    scaled_pixbuf = pixbuf.scale_simple(w,h,gtk.gdk.INTERP_NEAREST)
    ctx2.set_source_pixbuf(scaled_pixbuf,0,0)
    ctx2.paint()
    return imageSurface

def text_surface(text,w,h):
    textSurface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
    ctx = cairo.Context(textSurface)
    ctx.set_line_width(6)
    ctx.set_tolerance(.1)
    ctx.select_font_face('sans-serif')
    ctx.set_font_size(20)
    (x, y, width, height, dx, dy) = ctx.text_extents(text)
    ctx.set_source_rgb(0,0,0)

    x_margin = 10
    y_margin = 10
    ctx.translate(x_margin+x,y_margin+(-y))
    ctx.set_source_rgb(0,0,0)
    ctx.show_text(text)
    return textSurface

def white_background(ctx,w,h):
    ctx.set_source_rgb(1,1,1)
    ctx.rectangle(0,0,w,h)
    ctx.fill()

    
def expose(widget,event):
    _,_,w,h = widget.allocation
    pixmap = gtk.gdk.Pixmap(widget.window,w,h)
    
    cairo_test(pixmap,w,h)
    
    gc = gtk.gdk.GC(widget.window)
    widget.window.draw_drawable(gc, pixmap, 0,0, 0,0, -1,-1)
    
def key_handler(window,event):
    keyval = event.keyval
    state = event.state & gtk.accelerator_get_default_mod_mask()
    
    if keyval == keysyms.A:
        print keysyms.A

def main():
    window = gtk.Window()
    window.connect("destroy", gtk.main_quit)
    window.connect('key-press-event',key_handler)
    window.set_default_size(800,480)
    
    da = gtk.DrawingArea()
    
    da.connect('expose_event',expose)

    da.set_events(gtk.gdk.EXPOSURE_MASK
                   | gtk.gdk.LEAVE_NOTIFY_MASK
                   | gtk.gdk.BUTTON_PRESS_MASK
                   | gtk.gdk.BUTTON_RELEASE_MASK
                   | gtk.gdk.POINTER_MOTION_MASK
                   | gtk.gdk.POINTER_MOTION_HINT_MASK)

    window.add(da)
    window.show_all()
        
    gtk.main()


if __name__ == '__main__':
    main()