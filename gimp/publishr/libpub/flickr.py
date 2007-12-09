#!/usr/bin/env python

# Copyright (c) 2007 by the respective coders, see
# http://flickrapi.sf.net/
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import gtk

import libpub

##############################################
# XML parsing 
##############################################

import xml.dom.minidom
import mimetools
import md5
import urllib
import urllib2

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

##############################################
# Flickr API 
##############################################

class Flickr:
    def __init__(self,keyserver):
        self.keyserver = keyserver
        self.fHost = 'api.flickr.com'
        self.fRestURL = '/services/rest/'
        self.fUploadURL = '/services/upload/'
        
    def testResult(self,data):
        try:
            result = XMLNode.parseXML(data)
        except Exception, e:
            libpub.alert('Flickr call failed: error parsing response %s'%data)
            return None

        if result['stat'] != 'ok':
            libpub.alert('Flickr call failed: %s'%data)
            return None
        else:
            return result

    def upload(self, filename=None, jpegData=None, **params):
        if filename == None and jpegData == None or \
            filename != None and jpegData != None:
            libpub.alert('Upload: Invalid parameters')

        arg = self.keyserver.altcanvas.signParams(params)
        
        url = "http://" + self.fHost + self.fUploadURL

        # construct POST data
        boundary = mimetools.choose_boundary()
        body = ""

        # required params
        for a in ('api_key', 'auth_token', 'api_sig'):
            body += "--%s\r\n" % (boundary)
            body += "Content-Disposition: form-data; name=\""+a+"\"\r\n\r\n"
            body += "%s\r\n" % (arg[a])

        # optional params
        for a in ('title', 'description', 'tags', 'is_public', \
            'is_friend', 'is_family'):

            if arg.has_key(a):
                body += "--%s\r\n" % (boundary)
                body += "Content-Disposition: form-data; name=\""+a+"\"\r\n\r\n"
                body += "%s\r\n" % (arg[a])

        body += "--%s\r\n" % (boundary)
        body += "Content-Disposition: form-data; name=\"photo\";"
        body += " filename=\"%s\"\r\n" % filename
        body += "Content-Type: image/jpeg\r\n\r\n"

        if filename != None:
            fp = file(filename, "rb")
            data = fp.read()
            fp.close()
        else:
            data = jpegData

        postData = body.encode("utf_8") + data + \
            ("\r\n--%s--" % (boundary)).encode("utf_8")

        request = urllib2.Request(url)
        request.add_data(postData)
        request.add_header("Content-Type", \
            "multipart/form-data; boundary=%s" % boundary)
        response = urllib2.urlopen(request)
        data = response.read()

        result = self.testResult(data)
        
        if result != None:
            id = result.photoid[0].elementText
            return id
        else:
            return None
        
from libpub import SERVER,load_authtoken,save_authtoken

            
class FlickrObject:
    keyserver = None
    isConnected = False
    authtoken = None
    frob = None
    
    def connect(self):
        if not self.isConnected:
            self.keyserver = xmlrpclib.Server(SERVER)
            self.isConnected = True
        
    def __init__(self):
        authtoken = load_authtoken()
        if authtoken != None:
            self.authtoken = authtoken
            
    def has_auth(self):
        if self.authtoken:
            return True
        else:
            return False
            
    def get_authurl(self):
        self.connect()
        # get a frob
        self.frob = self.keyserver.altcanvas.getFrob()
            
        if self.frob == None:
            libpub.alert("Error connecting to keyserver")
            destroy()
        
        # get URL from backend
        authurl = self.keyserver.altcanvas.getAuthUrl(self.frob)
        
        if authurl == None:
            libpub.alert("Error connecting to keyserver")
            destroy()
            
        return authurl
    
    def get_authtoken(self):
        self.authtoken = self.keyserver.altcanvas.getAuthToken(self.frob)
        return self.authtoken
    
class FlickrRegisterBox(gtk.VBox):
    def __init__(self,parent):
        gtk.VBox.__init__(self)
        self.flickrObject = parent.flickrObject
        self.explainLabel = gtk.Label(
        'Please copy the following link and open it using your web browser.'+
        'Flickr will ask you to authorize AltCanvas to upload photos to your account.'+
        'You will have to click on "OK, I\'ll allow it" to be able to use this plugin.')
        self.explainLabel.set_width_chars(45)
        self.explainLabel.set_line_wrap(True)
        self.urlText = gtk.Entry()
        self.urlText.set_width_chars(45)
        self.doneButton = gtk.Button('Press when you have granted authorization to AltCanvas!')
        self.doneButton.set_border_width(5)
        self.doneButton.connect("clicked",parent.flickr_login_handler)
        
        self.set_spacing(15)
        self.pack_start(self.explainLabel)
        self.pack_start(self.urlText)
        self.pack_start(self.doneButton)
        self.set_border_width(30)
        self.show_all()
        
    def setup(self):
        authurl = self.flickrObject.get_authurl()
        
        self.urlText.set_text(authurl)
        self.urlText.select_region(0,-1)
        self.urlText.set_editable(False)
        
    def getauthtoken(self,widget,data=None):
        try:
            authtoken = self.flickrObject.get_authtoken()
            if authtoken != None:
                save_authtoken(authtoken)
                parent.authenticate(authtoken)
            else:
                libpub.alert("There was error retrieving Flickr Authentication token.\n"+
                      "Are you sure, you have authorized this application?\n"+
                      "Try again!")
        except Exception, e:
            libpub.alert("Network error while retrieving Auth Token: %s"%e)
     

    