import cairo

class Label:
    surface = None
    
    def __init__(self,text):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,400,200)
        ctx = cairo.Context(self.surface)
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