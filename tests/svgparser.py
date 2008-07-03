#!/usr/bin/python2.5

'''
import utils

fd = open('/photos/altimages/cartoons/test2.svg')
svg_content = ''
for line in fd:
    svg_content += line

svgnode = utils.XMLNode().parseXML(svg_content)

print '-----------'

print svgnode.g[0].g[1]['id']

print svgnode.g[0].elementText
'''

fd = open('/photos/altimages/cartoons/test2.svg')
svg_content = ''
for line in fd:
    svg_content += line


import xml.dom.minidom

dom = xml.dom.minidom.parseString(svg_content)


def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def handlePath(path):
    print '<< -------- path ------- >>'
    if not path.childNodes:
        print path.toxml()

def handleRect(rect):
    print '<< -------- rect ------- >>'
    if not rect.childNodes:
        print rect.toxml()

def handleG(g):
    print '<< -------- g ------- >>'
    if not g.childNodes:
        print g.toxml()

def handleSVG(svgdoc):
    obj_handlers = {
                    'g':handleG,
                    'path':handlePath,
                    'rect':handleRect
                   }
    for obj in obj_handlers.keys():
        for i in svgdoc.getElementsByTagName(obj):
            obj_handlers[obj](i)

handleSVG(dom)
