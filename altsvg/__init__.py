'''An alternative implementation of libaltsvg. This one is in python'''

from xml.etree.ElementTree import ElementTree

ns = "{http://www.w3.org/2000/svg}"
TAG_G = ns+'g'
TAG_PATH = ns+'path'
TAG_RECT = ns+'rect'

def process_path(elem):
    print elem.get('id')

def process_rect(elem):
    print elem.get('id')

def process_group(elem):
    for e in elem.getchildren():
        elem_processor_map[e.tag](e)

elem_processor_map = {
                        TAG_G:process_group,
                        TAG_PATH:process_path,
                        TAG_RECT:process_rect
                    }

def parse(filename):
    tree = ElementTree()
    tree.parse(filename)
    root_g = tree.find(TAG_G)
    process_group(root_g)

