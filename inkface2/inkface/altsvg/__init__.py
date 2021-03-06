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
TAG_METADATA        = SVG_NS+'metadata'
TAG_LINEARGRAD      = SVG_NS+'linearGradient'
TAG_RADIALGRAD      = SVG_NS+'radialGradient'
TAG_STOP            = SVG_NS+'stop'
TAG_G               = SVG_NS+'g'
TAG_PATH            = SVG_NS+'path'
TAG_RECT            = SVG_NS+'rect'
TAG_LINE            = SVG_NS+'line'
TAG_TEXT            = SVG_NS+'text'
TAG_TSPAN           = SVG_NS+'tspan'
TAG_IMAGE           = SVG_NS+'image'
TAG_INKSCAPE_LABEL  = INKSCAPE_NS+'label'
TAG_HREF            = XLINK_NS+'href'

import inkface.altsvg.draw
from inkface.altsvg.element import Element
from inkface.altsvg.style import LinearGradient, RadialGradient
from inkface.altsvg.style import parse_length
from inkface.altsvg.draw import NODE_DRAW_MAP


class VectorDoc:
    ''' 
    Class encapsulating a single SVG document 
       .. attribute:: width
       Width of SVG document (float)

       .. attribute:: height
       Height of SVG document (float)
    '''
    defs = {}
    def __init__(self, svgname):
        ''' load and parse SVG document, create ElementTree from the same '''
        self.svgfilepath = svgname
        self.tree = ElementTree()
        self.tree.parse(svgname)

        defs_node = self.tree.find(TAG_DEFS)

        # Add full path of SVG doc into defs. It is required for rendering
        # image elements, where linked image files need to be searched w.r.t. 
        # relative paths
        self.defs['docpath'] = svgname

        #
        # Gradient are defined by a tuple of stops.
        # Each stop is a tuple with first element offset and 
        # second being the style string
        #
        if defs_node is not None:
            for e in defs_node.getchildren():
                if e.tag == TAG_LINEARGRAD:
                    self.defs[e.attrib.get('id')] = \
                        LinearGradient(e)
                elif e.tag == TAG_RADIALGRAD:
                    self.defs[e.attrib.get('id')] = \
                        RadialGradient(e)

        self._implemented_node_types = \
            (TAG_G, TAG_RECT, TAG_PATH, TAG_TEXT, TAG_IMAGE)

    def __getattr__(self,key):
        if self.__dict__.has_key(key):
            return self.__dict__[key]

        if self.tree:
            root = self.tree.getroot()
            val = root.attrib.get(key)
            if val:
                if key is 'width' or key is 'height':
                    return parse_length(val)
                else:
                    return val
            else:
                raise AttributeError('Unknown attribute '+key)
                
        raise AttributeError('Unknown attribute '+key)
 
    def _get_element_nodes(self):
        for node in self.tree.getroot().getchildren():
            if node.tag == TAG_DEFS: continue

            if node.tag == TAG_METADATA: continue

            if node.tag not in self._implemented_node_types: continue

            if node.tag == TAG_G:
                for cnode in node.getchildren():
                    yield cnode
                continue

            yield node

        
    def get_elements(self):
        '''
            Returns list of :class:`inkface.altsvg.element.Element` objects \
            loaded from the SVG file.

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

        element = Element(None,self)
        in_backdrop = True
        elements = []
        for e in self._get_element_nodes():
            if in_backdrop and e.attrib.has_key(TAG_INKSCAPE_LABEL):
                in_backdrop = False

                if element.surface != None:
                    # Nothing got drawn on this element
                    elements.append(element)

                # Keep a reference to the backdrop surface, we will use
                # it as a scratch surface later
                backdrop_surface = element.surface


            if in_backdrop:
                element.add_node(e)
            else:
                element = Element(e,self) 
                element.render(scratch_surface=backdrop_surface)
                elements.append(element)

        if len(elements) == 0:
            ''' That means there were no TAG_INKSCAPE_LABEL elems 
                everything is in backdrop '''
            elements.append(element)
            
        return elements
        
    def get_qt_elements(self):
        from inkface.altsvg.qtelement import QtElement
        element = QtElement(None, self)
        in_backdrop = True
        elements = []

        for e in self._get_element_nodes():
            if in_backdrop and e.attrib.has_key(TAG_INKSCAPE_LABEL):
                in_backdrop = False

                if element.pixmap is not None:
                    elements.append(element)

                # Keep a reference to the backdrop surface, we will use
                # it as a scratch surface later
                backdrop_pixmap = element.pixmap

            if in_backdrop:
                element.add_node(e)
            else:
                element = QtElement(e, self)
                element.render()
                elements.append(element)

        if len(elements) == 0:
            elements.append(element)

        return elements

    def render_full(self, ctx):
        ''' 
        render the full SVG tree 

        :param ctx: cairo context on which to render the full SVG tree
        '''
        ctx.move_to(0, 0)
        for e in self._get_element_nodes():
            elem = Element(e,self)
            elem.raw_render(ctx, e)
            

