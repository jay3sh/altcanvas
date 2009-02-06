'''An alternative implementation of libaltsvg. This one is in python'''

#---------------------- EXPERIMENTAL -------------------------------

from xml.etree.ElementTree import ElementTree
import xml.etree

import re

svg_ns = "{http://www.w3.org/2000/svg}"
inkscape_ns = "{http://www.inkscape.org/namespaces/inkscape}"

TAG_SVG=svg_ns+'svg'
TAG_G = svg_ns+'g'
TAG_PATH = svg_ns+'path'
TAG_RECT = svg_ns+'rect'
TAG_INKSCAPE_LABEL = inkscape_ns+'label'

xml.etree.ElementTree._namespace_map['http://www.w3.org/2000/svg']='svg'

def search_elem(elem,name):
    try:
        if elem.attrib[TAG_INKSCAPE_LABEL] == name:
            return elem
    except KeyError, ke:
        pass


def search_group(elem,name):
    try:
        if elem.attrib[TAG_INKSCAPE_LABEL] == name:
            return elem
    except KeyError, ke:
        pass

    for e in elem.getchildren():
        if e.tag == TAG_G:
            res = search_group(e,name)
        else:
            res = search_elem(e,name)

        if res: return res

def get_elements(root_g,name=None):
    for e in root_g.getchildren():
        if not name:
            #yield e
            yield SVGElement(e.get('id'),e)
        else:
            if e.attrib.get(TAG_INKSCAPE_LABEL) == name:
                #yield e
                yield SVGElement(e.get('id'),e)
            else:
                continue

class SVGElement:
    surface = None
    def __init__(self,name,xmlnode):
        self.name = name
        self.xmlnode = xmlnode

    #
    # @return surface PyCairo surface with rendering of this SVG element
    #
    def get_surface(self):
        if not self.surface:
            self.render()

        return self.surface

    def render(self):
        r = node_renderer.get(self.xmlnode.tag,None)
        if r:
            r(self.xmlnode)
        else:
            print self.xmlnode.tag

def parse(filename):
    tree = ElementTree()
    tree.parse(filename)
    root_g = tree.find(TAG_G)

    for e in get_elements(root_g):
        print e.get_surface()

class SVGParser:
    def __init__(self,docname):
        self.tree = ElementTree()
        self.tree.parse(docname)

        #Find the first "g" tag and treat it as root "g" node
        root_g = self.tree.find(TAG_G)
        for e in root_g.getchildren():
            print e.attrib.get('id')

#---------------------- FORMAL -------------------------------

def render_rect(cr,node):
    cr.save()
    x = float(node.attrib.get('x'))
    y = float(node.attrib.get('y'))
    w = float(node.attrib.get('width'))
    h = float(node.attrib.get('height'))
    cr.rel_move_to(x,y)
    cr.rel_line_to(w,0)
    cr.rel_line_to(0,h)
    cr.rel_line_to(-w,0)
    cr.rel_line_to(0,-h)
    cr.stroke_preserve()
    cr.rel_move_to(-x,-y)
    cr.restore()

def render_path(cr,node):
    pathdata = node.attrib.get('d')
    pathdata = pathdata.replace(',',' ')

    tokens = pathdata.split()
    i = 0
    print tokens
    print len(tokens)
    while i < len(tokens):
        if tokens[i].isalpha():
            if tokens[i] == 'L':
                x = int(float(tokens[i+1]))
                y = int(float(tokens[i+2]))
                i += 3
                #line
                print 'line to %d %d'%(x,y)
                continue
            elif tokens[i] == 'M':
                x = int(float(tokens[i+1]))
                y = int(float(tokens[i+2]))
                i += 3
                #move
                print 'move to %d %d'%(x,y)
                continue
            elif tokens[i] == 'C':
                x1 = int(float(tokens[i+1]))
                y1 = int(float(tokens[i+2]))
                x2 = int(float(tokens[i+3]))
                y2 = int(float(tokens[i+4]))
                x = int(float(tokens[i+5]))
                y = int(float(tokens[i+6]))
                i += 7
                print 'curve to %d %d'%(x,y)
                continue
            elif tokens[i] == 'z':
                break

        # This should never be reached; 
        # but if the path data is malformed this will help from 
        # getting stuck in an infinite loop
        i += 1


    
node_renderer = \
    {
        TAG_RECT:render_rect,
        TAG_PATH:render_path
    }


#
# INTERFACE
#

#
# @return tree
#
def load(svgname):
    tree = ElementTree()
    tree.parse(svgname)
    return tree

#
# @return extract properties of the doc - returns a simple tuple for now
#
def extract_doc_data(tree):
    root = tree.getroot()
    try: 
        return(float(root.attrib.get('width')),
            float(root.attrib.get('height')))
    except ValueError,ve:
        print 'Error extracting SVG doc dimensions, falling back to 300x300'
        return ((300,300))

#
# @return elementlist
#
def extract_svg_elements(tree):
    root_g = tree.find(TAG_G)
    for e in root_g.getchildren():
        if e.attrib.has_key(TAG_INKSCAPE_LABEL):
            # Create SVG element for this node
            print e.attrib.get('id')

def render_full(cr,tree):
    root_g = tree.find(TAG_G)
    cr.move_to(0,0)
    render(cr,root_g)
        
def walk(tree):
    pass

def render(cr,node):
    for e in node.getchildren():
        dx = 0
        dy = 0
        transform = e.attrib.get('transform')
        if transform:
            pattern = '(\w+)\(([0-9-.]+),([0-9-.]+)\)'
            m = re.search(pattern,transform)
            if m: 
                dx = float(m.group(2))
                dy = float(m.group(3))

        cr.rel_move_to(int(dx),int(dy))

        if e.tag == TAG_G:
            render(cr,e)
        else:
            r = node_renderer.get(e.tag,None)
            if r:
                r(cr,e)
            else:
                print e.tag

        cr.rel_move_to(-int(dx),-int(dy))
