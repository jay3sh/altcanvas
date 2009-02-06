'''An alternative implementation of libaltsvg. This one is in python'''

#---------------------- EXPERIMENTAL -------------------------------

from xml.etree.ElementTree import ElementTree
import xml.etree

svg_ns = "{http://www.w3.org/2000/svg}"
inkscape_ns = "{http://www.inkscape.org/namespaces/inkscape}"

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

def render_rect(node):
    print 'Drawing rect '+\
            ' w:'+str(node.attrib.get('width'))+\
            ' h:'+str(node.attrib.get('height'))

def render_path(node):
    print 'Drawing path '+node.attrib.get('id')
    
node_renderer = \
    {
        TAG_RECT:render_rect,
        TAG_PATH:render_path
    }

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
        pass

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
# @return elementlist
#
def extract(tree):
    root_g = tree.find(TAG_G)
    for e in root_g.getchildren():
        if e.attrib.has_key(TAG_INKSCAPE_LABEL):
            # Create SVG element for this node
            print e.attrib.get('id')

def walk(tree):
    pass

def render(cr,node):
    pass
