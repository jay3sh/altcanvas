#!/usr/bin/python
import gtk
import cairo
import math


def cairo_test(pixmap,w,h):
    ctx = pixmap.cairo_create()
    white_background(ctx,w,h)
    
    surface = lingrad_surface(w-100,h-100)
    ctx.set_source_surface(surface,50,50)
    ctx.paint()
    
    
def lingrad_surface(w,h):
    lingradSurface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
    ctx = cairo.Context(lingradSurface)
    lingrad = cairo.LinearGradient(0.0,0.0,0.0,h)
    lingrad.add_color_stop_rgba(1,0,0,0,1)
    lingrad.add_color_stop_rgba(0,1,1,1,1)
    rect = ctx.rectangle(0,0,w,h)
    ctx.set_source(lingrad)
    ctx.fill()
    return lingradSurface

def white_background(ctx,w,h):
    ctx.set_source_rgb(1,1,1)
    ctx.rectangle(0,0,w,h)
    ctx.fill()
    
def cairo_test_1(pixmap,w,h):

    # Create the pixmap's context and paint it white
    ctx = pixmap.cairo_create()
    ctx.set_source_rgb(1,1,1)
    ctx.rectangle(0,0,w,h)
    ctx.fill()

    ctx.set_source_rgb(1,0.1,0.1)
    grad = cairo.LinearGradient(0,h,w,h)
    grad.add_color_stop_rgba(0,1,1,1,1)
    grad.add_color_stop_rgba(1,1,1,1,0)
    ctx.set_source(grad)
    
    #surface = get_gradient_surface(w-200,h-200)
    #ctx.set_source_surface(surface)
    
    
    
    ctx.rectangle(100,100,w-200,h-200)
    ctx.fill()
    
    
    
    
    
    '''
    ctx.set_source_rgb(1,0.1,0.1)
    #ctx.arc(100,100,50,0,math.pi*2)
    #ctx.fill()
    
    grad = cairo.LinearGradient(100,h-200,w-200,h-200)
    
    grad.add_color_stop_rgba(0,1,1,0.3,1)
    grad.add_color_stop_rgba(1,0,0,0,1)
    
    #ctx.set_source(grad)
    #ctx.rectangle(100,100,w-200,h-200)
    #ctx.mask_surface(surface)
    #ctx.paint()
    
    # draw image
    imgSurface = load_image('data/test4.png')
    ctx.mask_surface(surface)
    ctx.set_source_surface(imgSurface)
    ctx.paint()
    '''

def get_gradient_surface(w,h):
    gradSurface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
    gradCtx = cairo.Context(gradSurface)
    gradCtx.set_source_rgba(1,1,1,1)
    
    grad = cairo.LinearGradient(0,h,w,h)
    grad.add_color_stop_rgba(0,1,1,1,1)
    grad.add_color_stop_rgba(1,1,1,1,0)
    
    gradCtx.set_source(grad)
    gradCtx.fill()
    
    return gradSurface

def load_image(path):
    return cairo.ImageSurface.create_from_png(path)
    
def expose(widget,event):
    _,_,w,h = widget.allocation
    pixmap = gtk.gdk.Pixmap(widget.window,w,h)
    
    cairo_test(pixmap,w,h)
    
    gc = gtk.gdk.GC(widget.window)
    widget.window.draw_drawable(gc, pixmap, 0,0, 0,0, -1,-1)
    
def main():
    window = gtk.Window()
    window.connect("destroy", gtk.main_quit)
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