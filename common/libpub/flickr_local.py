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

##############################################
# XML parsing 
##############################################

import mimetools
import md5
import urllib
import urllib2

from libpub.utils.xmlparser import XMLNode

from libpub.flickrapi import Flickr


##########################################
#    Flickr Exception class
##########################################
class FlickrException(Exception):
    pass


from libpub import SERVER
import libpub

            
class FlickrObject:
    isConnected = False
    authtoken = None
    frob = None
    flickr = None
    
    def __init__(self):
        self.flickr = Flickr()
        authtoken = libpub.conf.get('FLICKR_TOKEN')
        if authtoken != None:
            self.authtoken = authtoken
            
    def has_auth(self):
        if self.authtoken:
            return True
        else:
            return False
            
    def get_authurl(self):
        # get a frob
        self.frob = self.flickr.auth_getFrob()
            
        if self.frob == None:
            libpub.alert("Error getting Frob")
            destroy()
        
        # get URL from backend
        authurl = self.flickr.getFlickrAuthURL(frob=self.frob)
        
        if authurl == None:
            libpub.alert("Error getting authurl")
            destroy()
            
        return authurl
    
    def get_authtoken(self):
        userinfo = self.flickr.auth_getToken(frob=self.frob)
        self.authtoken = userinfo.token
        if self.authtoken:
            libpub.conf.set('FLICKR_TOKEN',self.authtoken)
            return True
        else:
            libpub.alert("There was error retrieving Flickr Authentication token.\n"+
                  "Are you sure, you have authorized this application?\n"+
                  "Try again!")
            return False
        
    def get_photosets(self):
        userinfo = self.flickr.auth_checkToken(auth_token=self.authtoken)
        self.photosets = self.flickr.photosets_getList(user_id=userinfo.nsid)
        if self.photosets == None:
            self.photosets = []
        return self.photosets
    
    def createPhotoSet(self,imageID,curalbum):
        photosetID = self.flickr.photosets_create(
                title=curalbum,
                primary_photo_id=imageID,
                auth_token=self.authtoken)

        return photosetID
        
    def addPhoto2Set(self,imageID,setID):
        try:
            self.flickr.photosets_addPhoto(
                auth_token=self.authtoken,
                photo_id=imageID,
                photoset_id=setID)
            return True
        except Exception,e:
            libpub.alert('Exception adding photo to photoset: %e'%e)
            return False
    
    def setLicense(self,imageID,license_id='0'):
        self.flickr.photos_licenses_setLicense(
            photo_id=imageID,
            license_id=licenseID,
            auth_token=self.authtoken)
        return
       
    def getImageUrl(self,imageID): 
        info = self.flickr.photos_getInfo(
                    auth_token=self.authtoken,photo_id=imageID)
        if info == None:
            return None
        url = info.urls[0].url[0].elementText
        return url
    
    def upload(self,filename,title,description,is_public,tags,
                photoset=None,license_id=0):
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
        
        self.flickr.photos_licenses_setLicense(
            photo_id=imageID,
            license_id=license_id,
            auth_token=self.authtoken)
        
        url = self.getImageUrl(imageID)
        
        if url == None:
            raise FlickrException('Failed to get URL of uploaded image')
        
        # Find the photoset ID chosen from album drop down
        self.photosets = self.get_photosets()
        if self.photosets == None:
            self.photosets = []
            
        target_set_id = None
        for set in self.photosets:
            if set.title == photoset:
                target_set_id = set.id
                break
            
        # If user has left the photoset field blank then he doesn't want to
        # add the photo to any photoset. That's valid.
        if not photoset or photoset.strip() == '':
            return url
            
        # Create new photoset, it doesn't exist
        if target_set_id == None:
            target_set_id = self.createPhotoSet(imageID,photoset)
            if target_set_id == None:
                raise FlickrException("Failure creating new Photoset")
        else:
            # Add photo in an existing photoset
            if not self.addPhoto2Set(imageID,target_set_id):
                raise FlickrException("Failure adding photo to photoset")
                
        return url 
    

if __name__ == '__main__':
    fo = FlickrObject()
    url = fo.get_authurl()
    print url
    
