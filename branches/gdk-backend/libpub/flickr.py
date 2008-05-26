#!/usr/bin/env python

# Publishr to publish images on web
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

import gtk
import libpub
import xmlrpclib

##############################################
# XML parsing 
##############################################

import mimetools
import md5
import urllib
import urllib2

from libpub.utils.xmlparser import XMLNode


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
            raise FlickrException('%s'%result.err[0]['msg'])
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
        
##########################################
#    Flickr Exception class
##########################################
class FlickrException(Exception):
    pass


from libpub import SERVER
import libpub

            
class FlickrObject:
    keyserver = None
    isConnected = False
    authtoken = None
    frob = None
    flickr = None
    
    def connect(self):
        if not self.isConnected:
            self.keyserver = xmlrpclib.Server(SERVER)
            self.isConnected = True
            self.flickr = Flickr(self.keyserver)
        
    def __init__(self):
        authtoken = libpub.conf.get('FLICKR_TOKEN')
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
        if self.authtoken:
            libpub.conf.set('FLICKR_TOKEN',self.authtoken)
            return True
        else:
            libpub.alert("There was error retrieving Flickr Authentication token.\n"+
                  "Are you sure, you have authorized this application?\n"+
                  "Try again!")
            return False
        
    def get_photosets(self):
        self.connect()
        self.photosets = self.keyserver.altcanvas.getPhotoSets(self.authtoken)
        if self.photosets == None:
            self.photosets = []
        return self.photosets
    
    def createPhotoSet(self,imageID,curalbum):
        self.connect()
        return self.keyserver.altcanvas.createPhotoSet(
                                        self.authtoken,imageID,curalbum)
        
    def addPhoto2Set(self,imageID,setID):
        self.connect()
        return self.keyserver.altcanvas.addPhoto2Set(self.authtoken,imageID,setID)
    
    def setLicense(self,imageID,license_id='0'):
        self.connect()
        self.keyserver.altcanvas.setLicense(self.authtoken,imageID,license_id)
        return
       
    def getImageUrl(self,imageID): 
        self.connect()
        url = self.keyserver.altcanvas.getImageUrl(self.authtoken,imageID)
        return url
    
    def upload(self,filename,title,description,is_public,tags,license_id,photoset):
        self.connect()
        # Upload the photo
        imageID = self.flickr.upload(
                auth_token  = self.authtoken,
                filename    = filename,
                title       = title,
                description = description,
                is_public   = is_public,   
                tags        = tags)
        
        if imageID == None:
            raise FlickrException('NULL imageID returned')
        
        self.keyserver.altcanvas.setLicense(self.authtoken,imageID,license_id)
        
        url = self.keyserver.altcanvas.getImageUrl(self.authtoken,imageID)
        
        if url == None:
            raise FlickrException('Failed to get URL of uploaded image')
        
        # Find the photoset ID chosen from album drop down
        self.photosets = self.keyserver.altcanvas.getPhotoSets(self.authtoken)
        if self.photosets == None:
            self.photosets = []
            
        target_set_id = None
        for set in self.photosets:
            if set['title'] == photoset:
                target_set_id = set['id']
                break
            
        # If user has made the photoset field blank then he doesn't want to
        # add the photo to any photoset. That's a valid operation.
        if not photoset or photoset.strip() == '':
            return url
            
        # Create new photoset, it doesn't exist
        if target_set_id == None:
            target_set_id = self.keyserver.altcanvas.createPhotoSet(
                                        self.authtoken,imageID,photoset)
            if target_set_id == None:
                raise FlickrException("Failure creating new Photoset")
        else:
            # Add photo in an existing photoset
            if not self.keyserver.altcanvas.addPhoto2Set(
                                self.authtoken,imageID,target_set_id):
                raise FlickrException("Failure adding photo to photoset")
                
        return url 
    

    