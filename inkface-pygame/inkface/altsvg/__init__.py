#
# This file is part of altcanvas.
#
# altcanvas - SVG based GUI framework
# Copyright (C) 2009  Jayesh Salvi <jayeshsalvi@gmail.com>
#
# altcanvas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# altcanvas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with altcanvas.  If not, see <http://www.gnu.org/licenses/>.
#

'''An alternative implementation of libaltsvg. This one is in python'''

from xml.etree.ElementTree import ElementTree
import xml.etree
import re
import cairo


SVG_NS      = "{http://www.w3.org/2000/svg}"
INKSCAPE_NS = "{http://www.inkscape.org/namespaces/inkscape}"
XLINK_NS    = "{http://www.w3.org/1999/xlink}"

TAG_DEFS            = SVG_NS+'defs'
TAG_LINEARGRAD      = SVG_NS+'linearGradient'
TAG_RADIALGRAD      = SVG_NS+'radialGradient'
TAG_STOP            = SVG_NS+'stop'
TAG_G               = SVG_NS+'g'
TAG_PATH            = SVG_NS+'path'
TAG_RECT            = SVG_NS+'rect'
TAG_TEXT            = SVG_NS+'text'
TAG_TSPAN           = SVG_NS+'tspan'
TAG_INKSCAPE_LABEL  = INKSCAPE_NS+'label'
TAG_HREF            = XLINK_NS+'href'

import inkface.altsvg.draw
from inkface.altsvg.style import LinearGradient, RadialGradient
from inkface.altsvg.draw import NODE_DRAW_MAP

class Element:
    surface = None
    x = 0
    y = 0
    w = 0
    h = 0
    node = None

    def __init__(self,node,surface,x,y):
        self.node = node
        self.surface = surface
        self.x = x
        self.y = y
        self.w = self.surface.get_width()
        self.h = self.surface.get_height()

    def __getattr__(self,key):
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        elif self.node and key == 'label':
            return self.node.attrib.get(TAG_INKSCAPE_LABEL)
        elif self.node and self.node.attrib.has_key(key):
            return self.node.attrib.get(key)

        return None


class VectorDoc:
    ''' Class encapsulating a single SVG document '''
    defs = {}
    def __init__(self, svgname):
        ''' load and parse SVG document, create ElementTree from the same '''
        self.tree = ElementTree()
        self.tree.parse(svgname)

        defs_node = self.tree.find(TAG_DEFS)

        #
        # Gradient are defined by a tuple of stops.
        # Each stop is a tuple with first element offset and 
        # second being the style string
        #
        for e in defs_node.getchildren():
            if e.tag == TAG_LINEARGRAD:
                self.defs[e.attrib.get('id')] = \
                    LinearGradient(e)
            elif e.tag == TAG_RADIALGRAD:
                self.defs[e.attrib.get('id')] = \
                    RadialGradient(e)

    def __getattr__(self,key):
        if self.__dict__.has_key(key):
            return self.__dict__[key]

        if self.tree:
            root = self.tree.getroot()
            val = root.attrib.get(key)
            if val:
                return val
            else:
                raise AttributeError('Unknown attribute '+key)
                
 
    def get_elements(self):
        '''
            Algorithm to create Element objects from SVG doc:

            Start from the bottom most SVG node (i.e. beginning of doc),
            Keep looking for node with "inkscape:label" attr set. Until we
            get one of those, keep drawing the SVG nodes on the same cairo
            surface. This surface will make a single Element object with
            id "backdrop".

            After we find first "inkscape:label" attr in a node, we render
            each node on separate cairo surfaces (irrespective of "inkscape:
            label" attr is set for each of them or not)

            Creating a single backdrop element will help save memory on cairo
            surfaces. The fact that none of the bottom elements are named with
            "inkscape:label" by the designer, means that the program logic
            doesn't want to address to them programmatically, so they are
            essentially immutable.
        '''

        backdrop_surface = cairo.ImageSurface(
            cairo.FORMAT_RGB24,
            int(float(self.width)),
            int(float(self.height)))
        backdrop_ctx = cairo.Context(backdrop_surface)
        backdrop_ctx.move_to(0,0)
        root_g = self.tree.find(TAG_G)
        in_backdrop = True
        elements = []
        for e in root_g.getchildren():
            if in_backdrop and e.attrib.has_key(TAG_INKSCAPE_LABEL):
                in_backdrop = False
                elem = Element(None,backdrop_surface,0,0)
                elements.append(elem)

            if in_backdrop:
                self.__render(backdrop_ctx, e)
            else:
                # simulate rendering and get the extents
                ex1, ey1, ex2, ey2 = \
                    self.__render(backdrop_ctx, e, simulate=True)
                elem_surface = cairo.ImageSurface(
                    cairo.FORMAT_RGB24, int(ex2-ex1), int(ey2-ey1))

                elem_ctx = cairo.Context(elem_surface)
                elem_ctx.translate(-ex1,-ey1)

                # actually render the element
                self.__render(elem_ctx, e)
                elem = Element(e,elem_surface,ex1,ey1)
                elements.append(elem)

        if len(elements) == 0:
            ''' That means there were no TAG_INKSCAPE_LABEL elems 
                everything is in backdrop '''
            elem = Element(None,backdrop_surface,0,0)
            elements.append(elem)
            
        return elements
        
    def render_full(self, ctx):
        ''' render the full SVG tree '''
        root_g = self.tree.find(TAG_G)
        ctx.move_to(0, 0)
        for e in root_g.getchildren():
            self.__render(ctx, e)
            
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
