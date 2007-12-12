'''publishr plugin library '''

import os
import sys
import gtk

window = None
config = None
filename = '/tmp/test123.jpg'
CONFIG_FILE = ''

SERVER = 'http://fog.altcanvas.com/xmlrpc/'
VERSION = '0.2'

    
import xml.dom.minidom
class XMLNode:
    def __init__(self):
        """Construct an empty XML node."""
        self.elementName = ""
        self.elementText = ""
        self.attrib = {}
        self.xml = ""

    def __setitem__(self, key, item):
        """Store a node's attribute in the attrib hash."""
        self.attrib[key] = item

    def __getitem__(self, key):
        """Retrieve a node's attribute from the attrib hash."""
        return self.attrib[key]

    @classmethod
    def parseXML(cls, xml_str, store_xml=False):
        def __parseXMLElement(element, thisNode):
            """Recursive call to process this XMLNode."""
            thisNode.elementName = element.nodeName

            # add element attributes as attributes to this node
            for i in range(element.attributes.length):
                an = element.attributes.item(i)
                thisNode[an.name] = an.nodeValue

            for a in element.childNodes:
                if a.nodeType == xml.dom.Node.ELEMENT_NODE:
                    child = XMLNode()
                    try:
                        list = getattr(thisNode, a.nodeName)
                    except AttributeError:
                        setattr(thisNode, a.nodeName, [])

                    # add the child node as an attrib to this node
                    list = getattr(thisNode, a.nodeName)
                    list.append(child)

                    __parseXMLElement(a, child)

                elif a.nodeType == xml.dom.Node.TEXT_NODE:
                    thisNode.elementText += a.nodeValue
            
            return thisNode

        dom = xml.dom.minidom.parseString(xml_str)

        # get the root
        rootNode = XMLNode()
        if store_xml: rootNode.xml = xml_str

        return __parseXMLElement(dom.firstChild, rootNode)
    
    
    
    
class Config:
    map = None
    def __init__(self):
        self.CONFIG_FILE = None
        if sys.platform.find('win32') >= 0:
            self.CONFIG_FILE=os.getenv('USERPROFILE')+'\\.publishr'
        else:
            self.CONFIG_FILE=os.getenv('HOME')+'/.publishr'
        
        try:
            configf = open(self.CONFIG_FILE,'r')
        except IOError, ioe:
            self.map = None
            return
            
        xml = ''
        for line in configf:
            xml += line
        xmlresult = XMLNode.parseXML(xml)
        self.map = {}
        for param in xmlresult.param:
            key = param['name']
            value = param.elementText
            self.map[key] = value
                
        configf.close()
                
    def get(self,key):
        if self.map and key in self.map.keys():
            return self.map[key]
        return None
    
    def set(self,key,value):
        if not self.map:
            self.map = {}
        self.map[key] = value
        
        self.flush()
        
    def flush(self):
        try:
            configf = open(self.CONFIG_FILE,'w')
        except IOError, ioe:
            return None
        
        configf.write('<config>\n')
        for key in self.map.keys():
            configf.write('<param name="%s">%s</param>\n'%(key,self.map[key]))
        configf.write('</config>\n')
            
        configf.close()
            
        
def alert(msg,type=gtk.MESSAGE_ERROR):
    msgDlg = gtk.MessageDialog(window,
                    gtk.DIALOG_DESTROY_WITH_PARENT|gtk.DIALOG_MODAL,
                    type,
                    gtk.BUTTONS_CLOSE,
                    msg)
    msgDlg.connect("response", lambda dlg, resp: dlg.destroy())
    responseId = msgDlg.run()
    
    

def delete_event(widget,event,data=None):
    return False
    
def destroy(widget=None,data=None):
    gtk.main_quit()

def signout(widget=None,data=None):
    # Check if the file exists
    try:
        os.stat(CONFIG_FILE)
    except OSError, oe:
        return
    # Yes, it exists, delete it now
    try:
        os.remove(CONFIG_FILE)
    except IOError, ioe:
        alert('Error deleting flickr token. Check permissions on %s'%CONFIG_FILE)
    # Quit the GUI
    destroy()
