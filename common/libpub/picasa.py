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

        

import gtk

import libpub

########################################
# Picasaweb API
########################################
import libpub.atom as atom
import libpub.gdata.service
import libpub.gdata as gdata
import libpub.gdata.base
import libpub.gdata.photos.service

class PicasaException(Exception):
    pass

class PicasawebObject:
    picweb=None
    def __init__(self):
        self.picweb = libpub.gdata.photos.service.PhotosService()
        self.picweb.source = 'Publishr'
    
    def login(self,username,password):
        self.picweb.ClientLogin(username,password)
        
    def upload(self,filename,title,summary,tags,album):
        pws = self.picweb
        img = None
        
        # Get album feed
        albums = pws.GetUserFeed().entry
        
        # See if the album exists
        for a in albums:
            if a.title.text == album:
                img = pws.InsertPhotoSimple(
                    album_or_uri = a,
               	    title = title, 
                    summary = summary, 
                    filename_or_handle = filename)
        
        # The selected album was not found, create new one
        if not img:
            a = pws.InsertAlbum(title=album,summary=album)
            img = pws.InsertPhotoSimple(
                album_or_uri = a,
                title = title, 
                summary = summary, 
                filename_or_handle = filename)
            
        # Insert tag
        for tag in tags.split():
            pws.InsertTag(img,tag)
                
        return True
    