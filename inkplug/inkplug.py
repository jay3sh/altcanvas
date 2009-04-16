#!/usr/bin/env python

import os
import sys

sys.path.append('/usr/share/inkscape/extensions')
sys.path.append('/home/jayesh/altcanvas/inkface2')

import xml.etree.ElementTree
import zipfile

import random
random.seed()

from inkface.altsvg import VectorDoc


TMP_ZIPFILE = '/tmp/inkgui-'+str(random.randint(1,10000))+'.zip'

OUTPUT_DIR  = '/tmp/'
PNG_DIR     = os.path.join(OUTPUT_DIR,str(random.randint(1,10000)))
os.makedirs(PNG_DIR)


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
    elements = vDoc.get_elements()

    zip = zipfile.ZipFile(TMP_ZIPFILE,'w')
    
    root = xml.etree.ElementTree.Element('inkguiinfo')

    for elem in elements:
        try:
            png_name = elem.id+'.png'
        except AttributeError, ae:
            # this must be background
            png_name = 'bg.png'
    
        png_path = os.path.join(PNG_DIR, png_name)

        attrib = {
            'filename'  : png_name,
            'x'         : str(elem.x),
            'y'         : str(elem.y),
        }
        try:
            attrib['label'] = elem.label
        except AttributeError, ae:
            # Elements that are not labeled
            pass

        xml.etree.ElementTree.SubElement(root, tag='png', attrib=attrib)
        elem.surface.write_to_png(png_path)
    
        zip.write(png_path, 'inkgui/'+png_name)
    

    guiinfo_fname = os.path.join(PNG_DIR,'inkgui.xml')
    guiinfo = open(guiinfo_fname,'w')
    guiinfo.write(xml.etree.ElementTree.tostring(root))
    guiinfo.close()

    zip.write(guiinfo_fname, 'inkgui/'+'inkgui.xml')

    zip.close()

    zipf = open(TMP_ZIPFILE,'rb')
    for line in zipf.read():
        sys.stdout.write(line)


GenerateInk(sys.argv[1])


