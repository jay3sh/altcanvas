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
TAG_INKSCAPE_LABEL  = INKSCAPE_NS+'label'
TAG_HREF            = XLINK_NS+'href'

import draw
from style import LinearGradient, RadialGradient

class VectorDoc:
    defs = {}
    def __init__(self,svgname):
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
                '''
                if e.attrib.get(TAG_HREF):
                    grad = Gradient()
                    grad.type = Gradient.TYPE_LINEAR
                    grad.x1 = float(e.attrib.get('x1'))
                    grad.x2 = float(e.attrib.get('x2'))
                    grad.y1 = float(e.attrib.get('y1'))
                    grad.y2 = float(e.attrib.get('y2'))
                    grad.href = e.attrib.get(TAG_HREF)
                else:
                    stops = filter( \
                        lambda x: x.tag == TAG_STOP, e.getchildren())
                    grad = Gradient()
                    grad.stops = map ( \
                        lambda x: (x.attrib.get('offset'),
                                    x.attrib.get('style')),
                        stops)
                self.defs[e.attrib.get('id')] = grad
                '''
            elif e.tag == TAG_RADIALGRAD:
                self.defs[e.attrib.get('id')] = \
                    RadialGradient(e)
                '''
                if e.attrib.get(TAG_HREF):
                    grad = Gradient()
                    grad.type = Gradient.TYPE_RADIAL
                    grad.x1 = float(e.attrib.get('cx'))
                    grad.x2 = float(e.attrib.get('cy'))
                    grad.y1 = float(e.attrib.get('fx'))
                    grad.y2 = float(e.attrib.get('fy'))
                    grad.href = e.attrib.get(TAG_HREF)
                '''
 
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

    def render_full(self,ctx):
        ''' render the full SVG tree '''
        root_g = self.tree.find(TAG_G)
        ctx.move_to(0, 0)
        self.__render(ctx, root_g)
            
    def __render(self,ctx, node):
        ''' render individual SVG node '''
        for e in node.getchildren():
            dx = 0
            dy = 0
            transform = e.attrib.get('transform')
            if transform:
                pattern = '(\w+)\(([0-9-.]+),([0-9-.]+)\)'
                m = re.search(pattern, transform)
                if m: 
                    dx = float(m.group(2))
                    dy = float(m.group(3))
    
            ctx.rel_move_to(int(dx), int(dy))
    
            if e.tag == TAG_G:
                self.__render(ctx, e)
            else:
                r = draw.NODE_DRAW_MAP.get(e.tag, None)
                if r:
                    r(ctx, e, self.defs)
                else:
                    print e.tag
    
            ctx.rel_move_to(-int(dx), -int(dy))





