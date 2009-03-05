

import re

import cairo
from inkface.altsvg import TAG_INKSCAPE_LABEL,TAG_G,TAG_TSPAN
from inkface.altsvg.draw import NODE_DRAW_MAP

class Element:
    surface = None
    x = 0
    y = 0
    w = 0
    h = 0
    scale_factor = -1

    def __init__(self,node,vdoc):
        self.node = node
        self.vdoc = vdoc

        self.defs = vdoc.defs

    def __getattr__(self,key):
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        else:
            if self.__dict__.has_key('node'):
                node = self.__dict__['node']
            else:
                raise AttributeError('Unknown attribute: '+key)

            if node != None and key == 'label' and \
                node.attrib.has_key(TAG_INKSCAPE_LABEL):
                return node.attrib.get(TAG_INKSCAPE_LABEL)
            elif node != None and key == 'text':
                tspan = node.find('.//'+TAG_TSPAN)
                if tspan != None: 
                    return tspan.text
            elif node != None and self.node.attrib.has_key(key):
                return node.attrib.get(key)

        raise AttributeError('Unknown attribute: '+key)

    def __setattr__(self,key,value):
        # Search into the SVG node for the key
        if key == 'text' or key == 'label':
            if self.__dict__.has_key('node'):
                node = self.__dict__['node']
            else:
                raise Exception('node member is not set')

            if key == 'text':
                tspan = node.find('.//'+TAG_TSPAN)
                if tspan != None:
                    tspan.text = value
                else:
                    raise Exception('No text element found')
            elif key == 'label':
                node.set(TAG_INKSCAPE_LABEL,value)
            
        else:
            self.__dict__[key] = value

    def scale(self, factor):
        self.scale_factor = factor

    def add_node(self, node):
        if self.node == None:
            if self.surface == None:
                # This Element instance will be used later on to render
                # nodes later on. Create a surface of the size of whole
                # document. The oncoming nodes can be drawn on it
                self.surface = cairo.ImageSurface(
                    cairo.FORMAT_RGB24,
                    int(float(self.vdoc.width)),
                    int(float(self.vdoc.height)))
                self.x = 0
                self.y = 0
                self.w = self.surface.get_width()
                self.h = self.surface.get_height()

            ctx = cairo.Context(self.surface)
            ctx.move_to(0,0)

            self.__render(ctx, node)


    def render(self, scratch_surface=None):

        # If there was no old surface to scratch on, create one 
        if scratch_surface == None:
            scratch_surface = cairo.ImageSurface(
                cairo.FORMAT_RGB24,
                int(float(self.vdoc.width)),
                int(float(self.vdoc.height)))
            
        scratch_ctx = cairo.Context(scratch_surface)
        extents = self.__render(scratch_ctx, self.node, simulate=True)
        if extents == None:
            # There can be empty group nodes, hence no extents were returned
            # easy way to deal with them is to create surface of smallest
            # positive dimension on which nothing will be drawn
            # TODO: this might be handled in better way
            ex1, ey1, ex2, ey2 = (0, 0, 1, 1)
        else:
            ex1, ey1, ex2, ey2 = extents

        if self.scale_factor > 0:
            ex1,ey1,ex2,ey2 = \
                map(lambda x: x*self.scale_factor,(ex1,ey1,ex2,ey2))

        if (ex2-ex1) < 0 or (ey2-ey1) < 0:
            raise Exception('Invalid surface dim for %s: %f,%f'%\
                (self.node.get('id'),(ex2-ex1),(ey2-ey1)))

        self.surface = cairo.ImageSurface(
            cairo.FORMAT_RGB24, int(ex2-ex1), int(ey2-ey1))
        elem_ctx = cairo.Context(self.surface)
        elem_ctx.translate(-ex1,-ey1)

        if self.scale_factor > 0:
            elem_ctx.scale(self.scale_factor,self.scale_factor)

        self.__render(elem_ctx, self.node)

        self.x = ex1
        self.y = ey1
        self.w = self.surface.get_width()
        self.h = self.surface.get_height()


    def __render(self, ctx, e, simulate=False):
        ''' render individual SVG node '''
        x0 = None
        y0 = None
        transform = e.attrib.get('transform')
        transform_type = None
        if transform:
            pattern = '(\w+)\s*\(([0-9-.,]+)\)'
            m = re.search(pattern, transform)
            if m: 
                transform_type = m.group(1)
                transform_values = m.group(2)

                if transform_type == 'translate':
                    x0, y0 = \
                    map(lambda x: float(x), transform_values.split(','))
                elif transform_type == 'matrix':
                    xx, xy, yx, yy, x0, y0 = \
                    map(lambda x: float(x), transform_values.split(','))
            else:
                raise Exception('Unable to match transform')

        ctx.save()

        extents = None

        transform_matrix = None

        if transform_type == 'translate':
            transform_matrix = cairo.Matrix(1,0,0,1,x0,y0)
        elif transform_type == 'matrix':
            transform_matrix = cairo.Matrix(xx,xy,yx,yy,x0,y0)

        if transform_matrix:
            ctx.transform(transform_matrix)

        if e.tag == TAG_G:
            for sub_e in e.getchildren():
                new_extents = self.__render(ctx, sub_e, simulate)

                if simulate:
                    if new_extents == None:
                        ex1, ey1, ex2, ey2 = (0,0,0,0)
                    else:
                        ex1, ey1, ex2, ey2 = new_extents

                    # The following adjustment is questionable
                    # TODO
                    if transform_matrix:
                        new_extents = \
                            transform_matrix.transform_point(ex1,ey1)+\
                            transform_matrix.transform_point(ex2,ey2)

                    # /TODO

                    extents = self.__union(extents,new_extents)
        else:
            draw = NODE_DRAW_MAP.get(e.tag, None)
            if draw:
                new_extents = draw(ctx, e, self.defs, simulate)
                if simulate:
                    ex1, ey1, ex2, ey2 = new_extents
                    # The following adjustment is questionable
                    # TODO
                    if transform_matrix:
                        new_extents = \
                            transform_matrix.transform_point(ex1,ey1)+\
                            transform_matrix.transform_point(ex2,ey2)
                    # /TODO
                    extents = self.__union(extents,new_extents)
            else:
                raise Exception("Shape not implemented: "+e.tag)

        ctx.restore()

        if simulate:
            return extents

    def __union(self, extents,new_extents):
        if not extents:
            return new_extents

        ox1,oy1,ox2,oy2 = extents
        nx1,ny1,nx2,ny2 = new_extents

        if nx1 < ox1:
            x1 = nx1
        else:
            x1 = ox1

        if ny1 < oy1:
            y1 = ny1
        else:
            y1 = oy1

        if nx2 > ox2:
            x2 = nx2
        else:
            x2 = ox2

        if ny2 > oy2:
            y2 = ny2
        else:
            y2 = oy2

        return (x1, y1, x2, y2)
