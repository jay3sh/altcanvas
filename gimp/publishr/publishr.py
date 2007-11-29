#!/usr/bin/env python

# Gimp publishr plugin to publish images on web
# Copyright (C) 2007  Jayesh Salvi 
# http://www.altcanvas.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

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


#
# Acknowledgement for Picasaweb code:
#    The Picasaweb code that uses Google's gdata library to access Picasaweb Album
#    is derived from manatlan's code. 
#    It can be found at:
#    http://jbrout.python-hosting.com/file/trunk/plugins/multiexport/libs/picasaweb/__init__.py?rev=193
#


import pygtk
import gtk
import os
import sys
import mimetools
import md5
import urllib
import urllib2
import xmlrpclib
import re

from gimpfu import *

window = None
config = None
filename = '/tmp/test123.jpg'

SERVER = 'http://www.altcanvas.com/xmlrpc/'
VERSION = '0.2'

if sys.platform.find('win32') >= 0:
    CONFIG_FILE=os.getenv('USERPROFILE')+'\\.publishr'
else:
    CONFIG_FILE=os.getenv('HOME')+'/.publishr'

##############################################
# XML parsing 
##############################################

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
            alert('Flickr call failed: error parsing response %s'%data)
            return None

        if result['stat'] != 'ok':
            alert('Flickr call failed: %s'%data)
            return None
        else:
            return result

    def upload(self, filename=None, jpegData=None, **params):
        if filename == None and jpegData == None or \
            filename != None and jpegData != None:
            alert('Upload: Invalid parameters')

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
        
        
########################################
# Picasaweb API
########################################
import atom
import gdata.service
import gdata
import gdata.base

class PicasaWeb(gdata.service.GDataService):
    def __init__(self,username,password):
        gdata.service.GDataService.__init__(self)
        self.email = username
        self.password = password
        self.service = 'lh2'
        self.source = 'GDataService upload script'

        try:
            self.ProgrammaticLogin()
        except gdata.service.CaptchaRequired:
            raise Exception('Required Captcha')
        except gdata.service.BadAuthentication:
            raise Exception('Bad Authentication')
        except gdata.service.Error:
            raise Exception('Unknown Login Error')

    def getAlbums(self):
        try:
            albums = self.GetFeed(
                    'http://picasaweb.google.com/data/feed/api/user/'
                    + self.email
                    + '?kind=album&access=all'
                    )
            return [PicasaAlbum(self,a) for a in albums.entry]
        except:
            raise "GetAlbums() error ?!"


    def createAlbum(self,folderName,public=True):
        gd_entry = gdata.GDataEntry()
        gd_entry.title = atom.Title(text=folderName)
        gd_entry.category.append(atom.Category(
            scheme='http://schemas.google.com/g/2005#kind',
            term='http://schemas.google.com/photos/2007#album'))

        rights = public and "public" or "private"
        gd_entry.rights = atom.Rights(text=rights)

        ext_rights = atom.ExtensionElement( tag='access',
            namespace='http://schemas.google.com/photos/2007')
        ext_rights.text = rights
        gd_entry.extension_elements.append(ext_rights)

        album_entry = self.Post(gd_entry,
            'http://picasaweb.google.com/data/feed/api/user/' + self.email)

        return PicasaAlbum(self,album_entry)

class PicasaAlbum(object):
    name = property(lambda self:self.__ae.title.text)

    def __init__(self,gd,album_entry):
        self.__gd=gd
        self.__ae=album_entry

    def uploadPhoto(self,file,metadata=None):
        ms = gdata.MediaSource()

        try:
            ms.setFile(file, 'image/jpeg')
            link = self.__ae.link[0].href # self.__ae.GetFeedLink().href on created album
            media_entry = self.__gd.Post(metadata,link, media_source = ms)
            return PicasaImage(self.__gd,media_entry)
        except gdata.service.RequestError:
            return None 
        
class PicasaImage(object):
    def __init__(self,gd,photo_entry):
        self.__gd = gd
        self.__pe = photo_entry
        
    # broken
    def updatePhoto(self,metadata):
        try:
            photoid = self.__pe.id.text.rpartition('/')[2]
            media_entry = self.__gd.Post(metadata,photoid)
            return media_entry
        except gdata.service.RequestError,re:
            alert('Request error %s'%re)
            return None 
        
        
        
#########################################
#
# GUI and other plugin code
#
###########################################
            
def alert(msg,type=gtk.MESSAGE_ERROR):
    global window
    msgDlg = gtk.MessageDialog(window,
                    gtk.DIALOG_DESTROY_WITH_PARENT|gtk.DIALOG_MODAL,
                    type,
                    gtk.BUTTONS_CLOSE,
                    msg)
    msgDlg.connect("response", lambda dlg, resp: dlg.destroy())
    responseId = msgDlg.run()
    
def empty_window():
    global window
    for box in window.get_children():
        window.remove(box)
        
def load_authtoken():
    global CONFIG_FILE
    try:
        f = open(CONFIG_FILE,'r')
    except IOError, ioe:
        return None
    authtoken = f.readline()
    return authtoken

def save_authtoken(authtoken=None):
    global CONFIG_FILE
    try:
        f = open(CONFIG_FILE,'w')
    except IOError, ioe:
        alert("Error saving Flickr account info. "+
              "Please check that your home directory is writable to this application")
        return None
    f.write(authtoken)
    f.close()

class UploadGUI:
    def upload(self,widget,data=None):
        global filename
        
        title = self.titleEntry.get_text()
        buffer = self.descView.get_buffer()
        startiter,enditer = buffer.get_bounds()
        desc = buffer.get_text(startiter,enditer)
        tags = self.tagEntry.get_text()
        model = self.licenseCombo.get_model()
        active = self.licenseCombo.get_active()
        if active < 0:
            license = None
        else:
            license = model[active][0]
            
        # Upload to Flickr
        if self.type == 'FLICKR':
            flickrObject = self.webservice
            flickrObject.connect()
            flickr = Flickr(flickrObject.keyserver)
            imageID = flickr.upload(
	                filename=filename,
	                title=title,
	                auth_token=flickrObject.authtoken,
	                is_public='1',    # TODO programmable
	                tags=tags,
	                description=desc)
        
            if imageID != None:
            	url = flickrObject.keyserver.altcanvas.getImageUrl(imageID)
            	alert("Image upload was successful.\n(Flickr URL: %s)"%url,
                      gtk.MESSAGE_INFO)
            	destroy()
                
        # Upload to Picasaweb
        elif self.type == 'PICASAWEB':
            metadata = '''
                <entry xmlns='http://www.w3.org/2005/Atom'>
                    <title>%s</title>
                    <summary>%s</summary>
                    <category scheme="http://schemas.google.com/g/2005#kind"
                        term="http://schemas.google.com/photos/2007#photo"/>
                </entry>'''%(filename.rpartition(os.sep)[2],desc)
            picwebObject = self.webservice
            pw = picwebObject.picweb
            albumlist = pw.getAlbums()
            img = None
            for a in albumlist:
                if a.name == 'Gimp':
                    img = a.uploadPhoto(filename,metadata)
                    if img:
                        alert('Photo upload to Picasaweb was successful',gtk.MESSAGE_INFO)
                    else:
                        alert('Upload to Picasaweb failed')
                        return
            
            # The default album 'Gimp' was not found, create one
            if not img:
                a=pw.createAlbum("Gimp")
                img = a.uploadPhoto(filename,metadata)
                if img:
                    alert('Photo upload to Picasaweb was successful',gtk.MESSAGE_INFO)
                else:
                    alert('Upload to Picasaweb failed')
                    return
                
            destroy()
            tagmetadata = '''
                <entry xmlns='http://www.w3.org/2005/Atom'>
                    <title>altcanvas</title>
                    <category scheme="http://schemas.google.com/g/2005#kind"
                        term="http://schemas.google.com/photos/2007#tag"/>
                </entry>'''
            #result = img.updatePhoto(tagmetadata)
            

    def __init__(self,type=None,webservice=None):
        global window
        self.window = window
        self.type = type
        self.webservice = webservice

        # Define UI widgets
        titleLabel = gtk.Label('Title')
        self.titleEntry = gtk.Entry()
        titleLabel.show()
        self.titleEntry.show()

        descLabel = gtk.Label('Description')
        dsw = gtk.ScrolledWindow()
        dsw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.descView = gtk.TextView()
        self.descView.set_wrap_mode(gtk.WRAP_WORD)
        self.descView.set_accepts_tab(False)
        dsw.add(self.descView)
        descLabel.show()
        dsw.show()
        self.descView.show()

        tagLabel = gtk.Label('Tags')
        self.tagEntry = gtk.Entry()
        tagLabel.show()
        self.tagEntry.show()

        licenseLabel = gtk.Label('License')
        self.licenseCombo = gtk.combo_box_entry_new_text()
        licenses = [
            "All rights reserved",
            "Attribution-NonCommercial-ShareAlike License",
            "Attribution-NonCommercial License",
            "Attribution-NonCommercial-NoDerivs License",
            "Attribution License",
            "Attribution-ShareAlike License",
            "Attribution-NoDerivs License"
        ]
        for lic in licenses:
            self.licenseCombo.append_text(lic)
        licenseLabel.show()
        self.licenseCombo.set_active(0)
        self.licenseCombo.show()

        okButton = gtk.Button('Upload')
        okButton.connect("clicked",self.upload)
        cancelButton = gtk.Button('Quit')
        cancelButton.connect("clicked",destroy)
        signoutButton = gtk.Button('Sign out')
        signoutButton.connect("clicked",signout)
        okButton.show()
        cancelButton.show()
        signoutButton.show()

        # Pack all widgets
        titleBox = gtk.HBox()
        titleBox.pack_start(titleLabel)
        titleBox.pack_start(self.titleEntry)
        titleBox.show()
        titleBox.set_border_width(4)

        descBox = gtk.VBox()
        descLabelBox = gtk.HBox()
        descLabelBox.pack_start(descLabel,expand=False,fill=False)
        descLabelBox.show()
        descBox.pack_start(descLabelBox)
        descBox.pack_start(dsw)
        descBox.show()
        descBox.set_border_width(4)

        tagBox = gtk.HBox()
        tagBox.pack_start(tagLabel)
        tagBox.pack_start(self.tagEntry)
        tagBox.show()
        tagBox.set_border_width(4)

        licenseBox = gtk.HBox()
        licenseBox.pack_start(licenseLabel)
        licenseBox.pack_start(self.licenseCombo)
        licenseBox.show()

        inputBox = gtk.VBox()
        inputBox.pack_start(titleBox)
        inputBox.pack_start(descBox)
        inputBox.pack_start(tagBox)
        inputBox.pack_start(licenseBox)
        inputBox.show()
        inputBox.set_border_width(4)

        buttonBox = gtk.HBox()
        buttonBox.pack_start(okButton)
        buttonBox.pack_start(cancelButton)
        buttonBox.pack_start(signoutButton)
        buttonBox.show()
        buttonBox.set_border_width(4)

        windowBox = gtk.VBox()
        windowBox.pack_start(inputBox)
        windowBox.pack_start(buttonBox)
        windowBox.set_border_width(6)
        windowBox.show()
        
        if self.type == 'PICASAWEB':
            signoutButton.hide()
            titleBox.hide()
            self.tagEntry.set_text('not supported yet')
            self.tagEntry.set_state(gtk.STATE_INSENSITIVE)
            self.licenseCombo.append_text('not supported yet')
            model = self.licenseCombo.get_model()
            self.licenseCombo.set_active(len(model)-1)
            self.licenseCombo.set_state(gtk.STATE_INSENSITIVE)
        
        empty_window()

        self.window.add(windowBox)
        
class PicasawebObject:
    picweb=None
    def __init__(self):
        pass
    
class PicasawebRegisterBox(gtk.VBox):
    def __init__(self,picwebObject):
        gtk.VBox.__init__(self)
        self.picwebObject = picwebObject
        # Picasaweb Login widgets
        self.loginTitle = gtk.Label('Login to your Picasaweb (Google) account')
        self.usernameTitle = gtk.Label('Username')
        self.usernameEntry = gtk.Entry()
        self.usernameEntry.set_width_chars(15)
        self.passwordTitle = gtk.Label('Password')
        self.passwordEntry = gtk.Entry()
        self.passwordEntry.set_visibility(False)
        self.passwordEntry.set_width_chars(15)
        self.passwordExplainLabel = gtk.Label(
            "Your password is passed to Google's GDATA library which does "+
        	"the authentication over SSL connection. It is NOT sent anywhere "+
            "else on network or stored on disk in plaintext")
        self.passwordExplainLabel.set_width_chars(52)
        self.passwordExplainLabel.set_line_wrap(True)
        self.loginButton = gtk.Button('Login')
        self.loginButton.connect("clicked",self.login_handler)
        self.cancelButton = gtk.Button('Cancel')
        self.cancelButton.connect("clicked",destroy)
        
        self.usernameBox = gtk.HBox()
        self.usernameBox.pack_start(self.usernameTitle,expand=False)
        self.usernameBox.pack_start(self.usernameEntry,expand=False)
        self.usernameBox.set_homogeneous(True)
        self.passwordBox = gtk.HBox()
        self.passwordBox.pack_start(self.passwordTitle,expand=False)
        self.passwordBox.pack_start(self.passwordEntry,expand=False)
        self.passwordBox.set_homogeneous(True)
        self.buttonBox = gtk.HBox()
        self.buttonBox.pack_start(self.loginButton)
        self.buttonBox.pack_start(self.cancelButton)
            
        self.set_spacing(15)
        self.pack_start(self.loginTitle)
        self.pack_start(self.usernameBox)
        self.pack_start(self.passwordBox)
        self.pack_start(self.passwordExplainLabel)
        self.pack_start(self.buttonBox)
        self.set_border_width(30)
        
        self.show_all()
        
    def login_handler(self,widget,data=None):
        self.login(self.usernameEntry.get_text(), self.passwordEntry.get_text())
        
    def login(self,username,password):
        try:
            self.picwebObject.picweb = PicasaWeb(username,password)
        except Exception, e:
            alert('Login error: %s'%e)
        else:
            UploadGUI(type='PICASAWEB',webservice=self.picwebObject)
            
class FlickrObject:
    keyserver = None
    isConnected = False
    authtoken = None
    frob = None
    
    def connect(self):
        global SERVER
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
            alert("Error connecting to keyserver")
            destroy()
        
        # get URL from backend
        authurl = self.keyserver.altcanvas.getAuthUrl(self.frob)
        
        if authurl == None:
            alert("Error connecting to keyserver")
            destroy()
            
        return authurl
    
    def get_authtoken(self):
        self.authtoken = self.keyserver.altcanvas.getAuthToken(self.frob)
        return self.authtoken
    
class FlickrRegisterBox(gtk.VBox):
    def __init__(self,flickrObject):
        gtk.VBox.__init__(self)
        self.flickrObject = flickrObject
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
        self.doneButton.connect("clicked",self.getauthtoken)
        
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
                UploadGUI(type='FLICKR',webservice=self.flickrObject)
            else:
                alert("There was error retrieving Flickr Authentication token.\n"+
                      "Are you sure, you have authorized this application?\n"+
                      "Try again!")
        except Exception, e:
            alert("Network error while retrieving Auth Token: %s"%e)
        
    
class EntryGUI:
    frob = None
    openingBox = None
    flickrRegBox = None
    picwebRegBox = None
    def __init__(self,flickrObject,picwebObject):
        global window
        self.window = window
        
        # First screen widgets
        if flickrObject.has_auth():
            self.regFlickrButton = gtk.Button('Publish to Flickr!')
            self.regFlickrButton.connect("clicked",self.displayFlickr,flickrObject)
        else:
            self.regFlickrButton = gtk.Button('Sign into Flickr!')
            self.regFlickrButton.connect("clicked",self.displayFlickr,flickrObject)
        
        self.regPicwebButton = gtk.Button('Sign into Picasaweb!')
        self.regPicwebButton.connect("clicked",self.displayPicweb,picwebObject)
        
        self.cancelButton = gtk.Button('Later...')
        self.cancelButton.connect("clicked",destroy)
        
        # Container widgets
        self.openingBox = gtk.VBox()
        self.openingBox.set_spacing(15)
        self.openingBox.pack_start(self.regFlickrButton)
        self.openingBox.pack_start(self.regPicwebButton)
        self.openingBox.pack_start(self.cancelButton)
        self.openingBox.set_border_width(30)
        self.openingBox.show_all()
        
        self.window.add(self.openingBox)
                        
                        
    def displayFlickr(self,widget,data=None):
        try:
            empty_window()
            flickrObject = data
            if flickrObject.has_auth():
                uploadGUI = UploadGUI(type='FLICKR',webservice=flickrObject)
            else:
                self.flickrRegBox = FlickrRegisterBox(flickrObject)
                self.flickrRegBox.setup()
            	self.window.add(self.flickrRegBox)
        except Exception, e:
            alert("Flickr GUI: %s"%e)
            destroy()
        
    def displayPicweb(self,widget,data=None):
        try:
            empty_window()
            picwebObject = data
            self.picwebRegBox = PicasawebRegisterBox(picwebObject)
            self.window.add(self.picwebRegBox)
        except Exception, e:
            alert("Picasaweb GUI: %s"%e)
            destroy()
        

def delete_event(widget,event,data=None):
    return False
    
def destroy(widget=None,data=None):
    gtk.main_quit()
    
def signout(widget=None,data=None):
    global CONFIG_FILE
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

def publishr(image,drawable):
    global window
    global filename
    
    if image != None:
        # Check if file is dirty
	    if pdb.gimp_image_is_dirty(image):
	        alert("Please save the image before publishing.")
	        destroy()

	    # Check if flickr account is registered
	    filename = pdb.gimp_image_get_filename(image)
        # TODO better file name extension filtering
	    if(not (filename.lower().endswith('jpg') or 
	       filename.lower().endswith('jpeg') or 
	       filename.lower().endswith('gif'))):
	       alert("You have to save the file in jpeg or gif format before publishing") 
	       destroy()
    
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.connect("delete_event",delete_event)
    window.connect("destroy",destroy)
        
    flickrObject = FlickrObject()
    picwebObject = PicasawebObject()
    
    entryGUI = EntryGUI(flickrObject,picwebObject)

    window.show()
    gtk.main()
    
''' 
if __name__ == '__main__':
    publishr(None,None)
'''    
    

register(
    "python_fu_publish",
    "Image publishing plugin",
    "Image publishing plugin",
    "Jayesh Salvi",
    "Jayesh Salvi",
    "2007",
    "<Image>/File/_Publish on Web",
    "RGB*, GRAY*, INDEXED*",
    [],
    [],
    publishr)

main()
