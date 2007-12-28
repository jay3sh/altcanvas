
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


import os
import gtk
import pango

import libpub

from libpub.flickr import FlickrObject,FlickrException
from libpub.picasa import PicasawebObject,PicasawebRegisterBox
import libpub.gdata.photos.service.PicasaException as PicasaException

def empty_window():
    for box in libpub.window.get_children():
        libpub.window.remove(box)
        

class UploadGUI:
    ''' Main GUI container '''
    def __init__(self):
        self.window = libpub.window
        self.type = None
        self.webservice = None
        
        self.flickrObject = FlickrObject()
        self.picwebObject = PicasawebObject()
        
        # Service choice widgets
        self.flickrButton = gtk.Button('_Flickr')
        self.picwebButton = gtk.Button('_Picasaweb')
        
        self.flickrButton.connect("clicked",self.loadFlickr)
        self.picwebButton.connect("clicked",self.loadPicasaweb)
        
        self.introLabel = gtk.Label()
        self.introLabel.set_markup('\
<span font_family="sans" size="large" weight="heavy" >\
<span foreground="#000015">P</span>\
<span foreground="#00002A">u</span>\
<span foreground="#00003F">b</span>\
<span foreground="#000054">l</span>\
<span foreground="#000069">i</span>\
<span foreground="#00007E">s</span>\
<span foreground="#000093">h</span>\
<span foreground="#000000"> </span>\
<span foreground="#0000A8">o</span>\
<span foreground="#0000BD">n</span>\
<span foreground="#000000"> </span>\
<span foreground="#0000D2">w</span>\
<span foreground="#0000E7">e</span>\
<span foreground="#0000FC">b</span>\
<span foreground="#0000FF">!</span>\
</span>')

        # Pack all widgets
        serviceBox = gtk.VBox()
        serviceBox.pack_start(self.introLabel,expand=False)
        serviceBox.pack_start(self.flickrButton,expand=False)
        serviceBox.pack_start(self.picwebButton,expand=False)
        serviceBox.set_spacing(10)
        
        empty_window()
        
        serviceBox.set_border_width(15)
        serviceBox.show_all()
        self.window.add(serviceBox)
        
    def upload_dialog(self):
        # Define UI widgets
        
        albumLabel = None
        albums = None
        i = 0
        select_album = 0
        self.albumCombo = gtk.combo_box_entry_new_text()
        
        if self.type == 'FLICKR':
            albumLabel = gtk.Label('Photosets')
            albums = self.flickrObject.get_photosets()
            last_album = libpub.config.get('FLICKR_LAST_PHOTOSET')
            for album in albums:
                self.albumCombo.append_text(album['title'])
                if album['title'] == last_album:
                    select_album = i
                i += 1
            self.albumCombo.set_active(select_album)
            
            
        elif self.type == 'PICASAWEB':
            albumLabel = gtk.Label('Albums')
            pws = self.picwebObject.picweb
            albums = pws.GetUserFeed().entry
            last_album = libpub.config.get('PICASA_LAST_ALBUM')
            for album in albums:
                self.albumCombo.append_text(album.title.text)
                if album.name.text == last_album:
                    select_album = i
                i += 1
            self.albumCombo.set_active(select_album)
            
        
        titleLabel = gtk.Label('Title')
        self.titleEntry = gtk.Entry()
        
        descLabel = gtk.Label('Description')
        dsw = gtk.ScrolledWindow()
        dsw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.descView = gtk.TextView()
        self.descView.set_wrap_mode(gtk.WRAP_WORD)
        self.descView.set_accepts_tab(False)
        dsw.add(self.descView)

        tagLabel = gtk.Label('Tags')
        self.tagEntry = gtk.Entry()
        
        # Setup all the licenses
        licenseLabel = gtk.Label('License')
        self.licenseCombo = gtk.combo_box_entry_new_text()
        for lic in libpub.LicenseList:
            self.licenseCombo.append_text(lic[1])
        last_license = libpub.config.get('LAST_LICENSE_USED')
        
        if last_license:
            last_license_index = int(last_license) 
            if last_license_index >= 0 and  last_license_index < len(libpub.LicenseList)-1:
                self.licenseCombo.set_active(int(last_license))
            else:
                self.licenseCombo.set_active(0)
        else:
            self.licenseCombo.set_active(0)
        
        # Should the photo be public or private
        def privacy_toggled(togglebutton,param=None):
            if self.privacyCheck.get_active():
                self.is_public = '1'
            else:
                self.is_public = '0'
        
        self.privacyCheck = gtk.CheckButton(label='Public')
        self.privacyCheck.connect('toggled',privacy_toggled)
        
        # Recall what was the setting last time
        self.is_public =  libpub.config.get('LAST_PRIVACY_CHOICE') or '1'
        self.privacyCheck.set_active(self.is_public == '1')

        okButton = gtk.Button('Upload')
        okButton.connect("clicked",self.upload)
        cancelButton = gtk.Button('Quit')
        cancelButton.connect("clicked",libpub.destroy)
        signoutButton = gtk.Button('Sign out')
        signoutButton.connect("clicked",libpub.signout)
        
        # packing widgets
        albumBox = gtk.HBox()
        albumBox.pack_start(albumLabel)
        albumBox.pack_start(self.albumCombo)
        albumBox.set_border_width(4)
        
        titleBox = gtk.HBox()
        titleBox.pack_start(titleLabel)
        titleBox.pack_start(self.titleEntry)
        titleBox.set_border_width(4)

        descBox = gtk.VBox()
        descLabelBox = gtk.HBox()
        descLabelBox.pack_start(descLabel,expand=False,fill=False)
        descBox.pack_start(descLabelBox)
        descBox.pack_start(dsw)
        descBox.set_border_width(4)

        tagBox = gtk.HBox()
        tagBox.pack_start(tagLabel)
        tagBox.pack_start(self.tagEntry)
        tagBox.pack_start(self.privacyCheck)
        tagBox.set_border_width(4)

        licenseBox = gtk.HBox()
        licenseBox.pack_start(licenseLabel)
        licenseBox.pack_start(self.licenseCombo)

        inputBox = gtk.VBox()
        inputBox.pack_start(titleBox)
        inputBox.pack_start(descBox)
        inputBox.pack_start(albumBox)
        inputBox.pack_start(tagBox)
        inputBox.pack_start(licenseBox)
        inputBox.set_border_width(4)

        buttonBox = gtk.HBox()
        buttonBox.pack_start(okButton)
        buttonBox.pack_start(cancelButton)
        buttonBox.pack_start(signoutButton)
        buttonBox.set_border_width(4)
        

        uploadBox = gtk.VBox()
        uploadBox.pack_start(inputBox)
        uploadBox.pack_start(buttonBox)
        uploadBox.set_border_width(6)
        
        uploadBox.show_all()
        
        if self.type == 'PICASAWEB':
            signoutButton.hide()
            self.privacyCheck.hide()
            
            # Set the title to be the filename
            path_segments = libpub.filename.split(os.sep)
            self.title = path_segments[len(path_segments)-1]
            self.titleEntry.set_text(self.title)
            
            # Add a blank-license option to license choices. This will result
            # into appending nothing to the summary field about license info
            self.licenseCombo.append_text('Don\'t mention licensing info')
            model = self.licenseCombo.get_model()
            # Try to recall previous license choice
            last_license = libpub.config.get('LAST_LICENSE_USED')
            if last_license:
                self.licenseCombo.set_active(int(last_license))
            else:
                # choose blank-license option
                self.licenseCombo.set_active(len(model)-1)
            
        empty_window()
        self.window.add(uploadBox)
        
        
    def upload(self,widget,data=None):
        self.title = self.titleEntry.get_text()
        buffer = self.descView.get_buffer()
        startiter,enditer = buffer.get_bounds()
        desc = buffer.get_text(startiter,enditer)
        tags = self.tagEntry.get_text()
        
        # Get the index of chosen license 
        license_index = self.licenseCombo.get_active()
            
        # Get the chosen album name
        model = self.albumCombo.get_model()
        active = self.albumCombo.get_active()
        if active < 0:
            curalbum = self.albumCombo.get_active_text()
        else:
            curalbum = model[active][0]
            
        # Upload to Flickr
        if self.type == 'FLICKR':
            
            # Get license ID for chosen license
            if license_index > 0 and license_index < len(libpub.LicenseList):
                license_id = libpub.LicenseList[license_index][0]
            else:
                license_id = 0
                
            try:
                # Upload the photo
                url = self.flickrObject.upload(
                        filename = libpub.filename,
                        title = self.title,
                        description = desc,
                        is_public = self.is_public,
                        tags = tags,
                        license_id = str(license_id),
                        photoset = curalbum)
                
                if url:
                    # save the current album into config file
                    libpub.config.set('FLICKR_LAST_PHOTOSET',curalbum)
                    libpub.config.set('LAST_PRIVACY_CHOICE',self.is_public)
                    libpub.config.set('LAST_LICENSE_USED',license_index)
            
                    # success message
                    libpub.alert("Image upload was successful.\n(Flickr URL: %s)"%url,
                             gtk.MESSAGE_INFO)
                
            except FlickrException, fe:
                libpub.alert("Flickr Exception: %s"%fe)
                
            except Exception, e:
                libpub.alert("Upload exception: %s"%e)
                
            
        # Upload to Picasaweb
        elif self.type == 'PICASAWEB':
                
            if curalbum == None or curalbum.strip() == '':
                libpub.alert('Picasaweb doesn\'t support uploading photos \
without an album. If you don\'t have any album already, create one by typing \
a new album name in the "Albums" entry.')
                return
                
            # Determine the license text
            # Ignore the blank-license index 
            if license_index > 0 and license_index < len(libpub.LicenseList)-1:
                license_text = libpub.LicenseList[license_index][1]
                license_url = libpub.LicenseList[license_index][2]
                desc += '  [%s]'%(license_text)
                
            # this is the blank-index choice, preserve it
            elif license_index == len(libpub.LicenseList):
                pass
            
            # correct invalid values, it is possible for user entered text
            else:
                license_index = 0
                
            try:
                success = self.picwebObject.upload(
                        filename = libpub.filename, 
                        title = self.title,
                        summary = desc,
                        tags = tags,
                		album = curalbum)
            except PicasaException, pe:
                libpub.alert('Picasa Exception: %s'%pe)
            
            except Exception, e:
                libpub.alert('Upload exception: %s'%e)
            
                
            if success:
                # save the current album into config file
                libpub.config.set('PICASA_LAST_ALBUM',curalbum)
            	libpub.config.set('LAST_LICENSE_USED',license_index)
                libpub.alert('Successful upload to Picasaweb!',gtk.MESSAGE_INFO)
            
        # Cleanup the GUI
        libpub.destroy()
            
            
    def loadFlickr(self,widget,data=None):
        self.type = 'FLICKR'
        if self.flickrObject.has_auth():
            self.upload_dialog()
        else:
            self.displayFlickrLogin()
            
    def loadPicasaweb(self,widget,data=None):
        self.type = 'PICASAWEB'
        self.displayPicwebLogin()
    
    def displayPicwebLogin(self):
        try:
            empty_window()
            self.picwebRegBox = PicasawebRegisterBox(self)
            self.window.add(self.picwebRegBox)
        except Exception, e:
            libpub.alert("Picasaweb GUI: %s"%e)
            libpub.destroy()
        
    def displayFlickrLogin(self):
        try:
            empty_window()
            self.flickrRegBox = FlickrRegisterBox(self)
            self.flickrRegBox.setup()
            self.window.add(self.flickrRegBox)
        except Exception, e:
            libpub.alert("Flickr GUI: %s"%e)
            libpub.destroy()
            
        
class FlickrRegisterBox(gtk.VBox):
    def __init__(self,parent):
        gtk.VBox.__init__(self)
        self.parentgui = parent
        self.flickrObject = self.parentgui.flickrObject
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
        self.doneButton.connect("clicked",self.login_handler)
        
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
        
    def login_handler(self,widget,data=None):
        try:
            if self.flickrObject.get_authtoken():
                self.parentgui.upload_dialog()
        except Exception, e:
            libpub.alert("Unhandled exception while Flickr login: %s"%e)
     
        
