'''An alternative implementation of libaltsvg. This one is in python'''

import xml.dom.minidom

ns = "{http://www.w3.org/2000/svg}"
depth = 0

def process_element(node):
    global depth 
    depth += 1
    if node.nodeName == 'g':
        for n in node.childNodes:
            process_element(n)
    elif node.nodeName.startswith('#'):
        pass
    else:
        print '  '*depth+node.getAttribute('id')

    depth -= 1

def process_tree(element):
    global depth 
    depth += 1
    for e in element.getchildren():
        if e.tag[len(ns):] == 'g':
            process_tree(e)
        else:
            print '  '*depth+e.get('id')
    depth -= 1


def parse(filename):
    '''
    dom = xml.dom.minidom.parse(filename)
    root = dom.getElementsByTagName('g')[0]
    process_element(root)
    '''

    from xml.etree.ElementTree import ElementTree
    tree = ElementTree()
    tree.parse(filename)
    rootelem = tree.find(ns+'g')
    process_tree(rootelem)

