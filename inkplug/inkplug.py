#!/usr/bin/env python

import os
import sys

sys.path.append('/usr/share/inkscape/extensions')

import subprocess
import xml.etree.ElementTree
import zipfile

import random
random.seed()

from xml.etree.ElementTree import ElementTree

TMP_ZIPFILE = '/tmp/inkgui-'+str(random.randint(1,10000))+'.zip'

OUTPUT_DIR  = '/tmp/'
PNG_DIR     = os.path.join(OUTPUT_DIR,str(random.randint(1,10000)))
os.makedirs(PNG_DIR)

SVG_NS      = "{http://www.w3.org/2000/svg}"
INKSCAPE_NS = "{http://www.inkscape.org/namespaces/inkscape}"
XLINK_NS    = "{http://www.w3.org/1999/xlink}"

TAG_DEFS            = SVG_NS+'defs'
TAG_METADATA        = SVG_NS+'metadata'
TAG_G               = SVG_NS+'g'
TAG_INKSCAPE_LABEL  = INKSCAPE_NS+'label'

class VectorDoc:
    ''' Class encapsulating a single SVG document '''
    defs = {}
    def __init__(self, svgname):
        ''' load and parse SVG document, create ElementTree from the same '''

        self.svgfilepath = svgname
        self.tree = ElementTree()
        self.tree.parse(svgname)

    def get_elements(self):
        for node in self.tree.getroot().getchildren():
            if node.tag == TAG_DEFS: continue

            if node.tag == TAG_METADATA: continue

            if node.tag == TAG_G:
                for cnode in node.getchildren():
                    yield cnode
                continue

            yield node

def alert(msg):
    import gtk
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    msgDlg = gtk.MessageDialog(window,
                gtk.DIALOG_DESTROY_WITH_PARENT|gtk.DIALOG_MODAL,
                gtk.MESSAGE_ERROR,
                gtk.BUTTONS_CLOSE,
                msg)
    msgDlg.connect("response", lambda dlg, resp: dlg.destroy())
    responseId = msgDlg.run()
 

def GenerateInk(svgname):

    vDoc = VectorDoc(svgname)
    zip = zipfile.ZipFile(TMP_ZIPFILE,'w')

    root = xml.etree.ElementTree.Element('inkguiinfo')

    debug = open("/tmp/debug.txt","w")

    for node in vDoc.get_elements():
        id = node.get('id')
        if id == 'base': continue
        label = node.get(TAG_INKSCAPE_LABEL)
        png_name = id+".png"
        png_path = os.path.join(PNG_DIR, png_name)

        attrib = {
            'filename'  : png_name,
        }
        if label:
            attrib['label'] = label

        # Generate PNG
        command = ['/usr/bin/inkscape','--export-id-only',
                    '-i', id, '-e', png_path, '-f', svgname]
        of = open("/tmp/cout.txt","w")
        ef = open("/tmp/cerr.txt","w")
        pid = subprocess.Popen(command, stdout=of, stderr=ef)
        pid.wait()
        of.close()
        ef.close()

        # Find X
        command = ['/usr/bin/inkscape','-X', '--query-id',
                    id, '-f', svgname]
        of = open("/tmp/cout.txt","w")
        ef = open("/tmp/cerr.txt","w")
        pid = subprocess.Popen(command, stdout=of, stderr=ef)
        pid.wait()
        of.close()
        ef.close()
        of = open("/tmp/cout.txt","r")
        xvalue = of.read()
        of.close()
        debug.write(xvalue+"\n")

        # Find Y
        command = ['/usr/bin/inkscape','-Y', '--query-id',
                    id, '-f', svgname]
        of = open("/tmp/cout.txt","w")
        ef = open("/tmp/cerr.txt","w")
        pid = subprocess.Popen(command, stdout=of, stderr=ef)
        pid.wait()
        of.close()
        ef.close()
        of = open("/tmp/cout.txt","r")
        yvalue = of.read()
        of.close()
        debug.write(yvalue+"\n")
 
        attrib['x'] = xvalue
        attrib['y'] = yvalue

        debug.write(str(command)+"\n")

        debug.write(str(attrib)+"\n")
        xml.etree.ElementTree.SubElement(root, tag='png', attrib=attrib)
 
 
        zip.write(png_path, png_name)

    debug.close()

    guiinfo_fname = os.path.join(PNG_DIR,'inkgui.xml')
    guiinfo = open(guiinfo_fname,'w')
    guiinfo.write(xml.etree.ElementTree.tostring(root))
    guiinfo.close()

    zip.write(guiinfo_fname, 'inkgui.xml')

    zip.close()

    zipf = open(TMP_ZIPFILE,'rb')
    for line in zipf.read():
        sys.stdout.write(line)


GenerateInk(sys.argv[1])


