# This file is part of altcanvas.
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

def load_style(style_str):
    ''' Parse and load style from style string '''
    style = {}
    for style_attr in style_str.strip().split(';'):
        name, value = style_attr.split(':')
        style[name] = value
    return style

def apply_style(ctx, style):
    ''' Modify given contex according to the style '''
    if style.has_key('stroke-width'):
        ctx.set_line_width(float(style['stroke-width']))
    if style.has_key('stroke-miterlimit'):
        ctx.set_miter_limit(float(style['stroke-miterlimit']))

def render_rect(ctx, node):
    ''' Render 'rect' SVG element '''
    ctx.save()

    style_str = node.attrib.get('style')
    if style_str:
        style = load_style(style_str)
        if style:
            apply_style(ctx, style)

    x = float(node.attrib.get('x'))
    y = float(node.attrib.get('y'))
    w = float(node.attrib.get('width'))
    h = float(node.attrib.get('height'))
    ctx.rel_move_to(x, y)
    ctx.rel_line_to(w, 0)
    ctx.rel_line_to(0, h)
    ctx.rel_line_to(-w, 0)
    ctx.rel_line_to(0, -h)
    ctx.stroke_preserve()
    ctx.rel_move_to(-x, -y)

    ctx.restore()

def render_path(ctx, node):
    ''' Render 'path' SVG element '''
    ctx.save()

    style_str = node.attrib.get('style')
    if style_str:
        style = load_style(style_str)
        if style:
            apply_style(ctx, style)

    pathdata = node.attrib.get('d')
    pathdata = pathdata.replace(',',' ')

    dx, dy = ctx.get_current_point()

    tokens = pathdata.split()
    i = 0
    while i < len(tokens):
        if tokens[i].isalpha():
            if tokens[i] == 'L':
                x = int(float(tokens[i+1]))
                y = int(float(tokens[i+2]))
                i += 3
                ctx.line_to(x+dx, y+dy)
                continue
            elif tokens[i] == 'M':
                x = int(float(tokens[i+1]))
                y = int(float(tokens[i+2]))
                i += 3
                ctx.move_to(x+dx, y+dy)
                continue
            elif tokens[i] == 'C':
                x1 = int(float(tokens[i+1]))
                y1 = int(float(tokens[i+2]))
                x2 = int(float(tokens[i+3]))
                y2 = int(float(tokens[i+4]))
                x = int(float(tokens[i+5]))
                y = int(float(tokens[i+6]))
                i += 7
                ctx.curve_to(x1+dx, y1+dy, x2+dx, y2+dy, x+dx, y+dy)
                continue
            elif tokens[i] == 'z':
                break

        # This should never be reached; 
        # but if the path data is malformed this will help from 
        # getting stuck in an infinite loop
        i += 1

    ctx.stroke_preserve()
    ctx.restore()

    
NODE_RENDERER = \
    {
        TAG_RECT:render_rect,
        TAG_PATH:render_path
    }


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
            r = NODE_RENDERER.get(e.tag, None)
            if r:
                r(ctx, e)
            else:
                print e.tag

        ctx.rel_move_to(-int(dx), -int(dy))
