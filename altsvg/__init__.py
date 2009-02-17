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

import altsvg.draw
from altsvg.style import LinearGradient, RadialGradient

class Element:
    surface = None

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
                
 
    def get_doc_props(self):
        ''' extract properties of the doc - returns a simple tuple for now '''
        root = self.tree.getroot()
        try: 
            return(float(root.attrib.get('width')),
                float(root.attrib.get('height')))
        except ValueError, ve:
            print 'Error extracting SVG doc dimensions "%s", \
                falling back to 300x300' % str(ve)
            return ((300, 300))

    def get_svg_elements(self):
        ''' 
        find SVG elements with INKSCAPE_LABEL set and export them as 
        SVGElement objects 
        '''
        root_g = self.tree.find(TAG_G)
        for e in root_g.getchildren():
            if e.attrib.has_key(TAG_INKSCAPE_LABEL):
                # Create SVG element for this node
                print e.attrib.get('id')

    def get_elements(self):
        backdrop_surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32,
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
                elem = Element()
                elem.surface = backdrop_surface
                elements.append(elem)
                break

            if in_backdrop:
                r = altsvg.draw.NODE_DRAW_MAP.get(e.tag, None)
                if r:
                    r(backdrop_ctx, e, self.defs)
                else:
                    raise Exception("Shape not implemented: "+e.tag)

        return elements
        
    def render_full(self, ctx):
        ''' render the full SVG tree '''
        root_g = self.tree.find(TAG_G)
        ctx.move_to(0, 0)
        self.__render(ctx, root_g)
            
    def __render(self, ctx, node):
        ''' render individual SVG node '''
        for e in node.getchildren():
            dx = 0
            dy = 0
            transform = e.attrib.get('transform')
            transform_type = None
            if transform:
                pattern = '(\w+)\s*\(([0-9-.,]+)\)'
                m = re.search(pattern, transform)
                if m: 
                    transform_type = m.group(1)
                    transform_values = m.group(2)

                    if transform_type == 'translate':
                        dx, dy = \
                        map(lambda x: float(x), transform_values.split(','))
                    elif transform_type == 'matrix':
                        xx, xy, yx, yy, x0, y0 = \
                        map(lambda x: float(x), transform_values.split(','))
                else:
                    raise Exception('Unable to match transform')
    
            ctx.save()

            if transform_type == 'translate':
                ctx.set_matrix(cairo.Matrix(1,0,0,1,dx,dy))
            elif transform_type == 'matrix':
                ctx.set_matrix(cairo.Matrix(xx,xy,yx,yy,x0,y0))
    
            if e.tag == TAG_G:
                self.__render(ctx, e)
            else:
                r = altsvg.draw.NODE_DRAW_MAP.get(e.tag, None)
                if r:
                    r(ctx, e, self.defs)
                else:
                    raise Exception("Shape not implemented: "+e.tag)
    
            ctx.restore()





