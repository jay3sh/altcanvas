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

TAG_SVG             = SVG_NS+'svg'
TAG_G               = SVG_NS+'g'
TAG_PATH            = SVG_NS+'path'
TAG_RECT            = SVG_NS+'rect'
TAG_INKSCAPE_LABEL  = INKSCAPE_NS+'label'

import draw

#
# INTERFACE
#

def load(svgname):
    ''' load and parse SVG document, create ElementTree from the same '''
    tree = ElementTree()
    tree.parse(svgname)
    return tree

def extract_doc_data(tree):
    ''' extract properties of the doc - returns a simple tuple for now '''
    root = tree.getroot()
    try: 
        return(float(root.attrib.get('width')),
            float(root.attrib.get('height')))
    except ValueError, ve:
        print 'Error extracting SVG doc dimensions "%s", \
            falling back to 300x300' % str(ve)
        return ((300, 300))

#
# @return elementlist
#
def extract_svg_elements(tree):
    ''' 
    find SVG elements with INKSCAPE_LABEL set and export them as SVGElement 
    objects 
    '''
    root_g = tree.find(TAG_G)
    for e in root_g.getchildren():
        if e.attrib.has_key(TAG_INKSCAPE_LABEL):
            # Create SVG element for this node
            print e.attrib.get('id')

def render_full(ctx, tree):
    ''' render the full SVG tree '''
    root_g = tree.find(TAG_G)
    ctx.move_to(0, 0)
    render(ctx, root_g)
        
def render(ctx, node):
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
            render(ctx, e)
        else:
            r = draw.NODE_DRAW_MAP.get(e.tag, None)
            if r:
                r(ctx, e)
            else:
                print e.tag

        ctx.rel_move_to(-int(dx), -int(dy))
