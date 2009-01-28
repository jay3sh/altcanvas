'''An alternative implementation of libaltsvg. This one is in python'''

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


def parse(filename):
    tree = ElementTree()
    tree.parse(filename)
    root_g = tree.find(TAG_G)
    elem = search_group(root_g,'gObject')
    if elem:    
        print elem.attrib['id']
    else:
        print 'no elem found'

