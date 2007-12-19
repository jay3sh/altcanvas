import os
import gtk
import pango

import libpub

from libpub.flickr import FlickrObject,FlickrRegisterBox
from libpub.picasa import PicasawebObject,PicasawebRegisterBox

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
            
            #if last_album == None:
            #   self.albumCombo.prepend_text('<new-photoset>')
            #   self.albumCombo.set_active(0)
            
        elif self.type == 'PICASAWEB':
            albumLabel = gtk.Label('Albums')
            pws = self.picwebObject.picweb
            albumFeed = pws.GetAlbumFeed()
            last_album = libpub.config.get('PICASA_LAST_ALBUM')
            for album in albumFeed.entry:
                self.albumCombo.append_text(album.name.text)
                if album.name.text == last_album:
                    select_album = i
                i += 1
            self.albumCombo.set_active(select_album)
            
            #if last_album == None:
            #   self.albumCombo.prepend_text('<new-album>')
            #   self.albumCombo.set_active(0)
        
        
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
        self.licenseCombo.set_active(0)
        
        self.privacyCheck = gtk.CheckButton(label='Public')

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
            titleBox.hide()
            self.licenseCombo.append_text('not supported yet')
            self.privacyCheck.hide()
            model = self.licenseCombo.get_model()
            self.licenseCombo.set_active(len(model)-1)
            self.licenseCombo.set_state(gtk.STATE_INSENSITIVE)
            
        empty_window()
        self.window.add(uploadBox)
        
        
    def upload(self,widget,data=None):
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
            
        model = self.albumCombo.get_model()
        active = self.albumCombo.get_active()
        if active < 0:
            curalbum = self.albumCombo.get_active_text()
        else:
            curalbum = model[active][0]
            
        # Upload to Flickr
        if self.type == 'FLICKR':
            
            # Upload the photo
            imageID = self.flickrObject.upload(
                    filename=libpub.filename,
                    title=title,
                    auth_token=self.flickrObject.authtoken,
                    is_public='1',    # TODO programmable
                    tags=tags,
                    description=desc)
            
            url = self.flickrObject.getImageUrl(imageID)
            
            if url == None:
                libpub.alert("Image upload failed")
                libpub.destroy()
            
            # Find the photoset ID chosen from album drop down
            photosets = self.flickrObject.get_photosets()
            target_set_id = None
            for set in photosets:
                if set['title'] == curalbum:
                    target_set_id = set['id']
                    break
                
            # Create new photoset, it doesn't exist
            if target_set_id == None:
                target_set_id = self.flickrObject.createPhotoSet(imageID,curalbum)
                if target_set_id == None:
                    libpub.alert("Failure creating new Photoset")
            else:
                # Add photo in an existing photoset
                success = self.flickrObject.addPhoto2Set(imageID,target_set_id)
                
                if not success:
                    libpub.alert("Failure adding photo to photoset")
                    
            # save the current album into config file
            libpub.config.set('FLICKR_LAST_PHOTOSET',curalbum)
        
            libpub.alert("Image upload was successful.\n(Flickr URL: %s)"%url,
                         gtk.MESSAGE_INFO)
            libpub.destroy()
                
        # Upload to Picasaweb
        elif self.type == 'PICASAWEB':
            title = libpub.filename.rpartition(os.sep)[2]
            pws = self.picwebObject.picweb
            albumFeed = pws.GetAlbumFeed()
            img = None
            for a in albumFeed.entry:
                if a.name.text == curalbum:
                    uri = a.GetFeedLink().href
                    try:
                        img = pws.InsertPhoto(title=title,summary=desc,album_uri=uri,
                            filename_or_handle=libpub.filename)
                    except Exception, e:
                        libpub.alert('Upload to Picasaweb failed: %s'%e)
                        libpub.destroy()
                        
                    if img:
                        libpub.alert('Photo upload to Picasaweb was successful',gtk.MESSAGE_INFO)
            
            # The selected album was not found, create one
            if not img:
                try:
                    a = pws.InsertAlbum(title=curalbum,summary=None)
                    uri = a.GetFeedLink().href
                    img = pws.InsertPhoto(title=title,summary=desc,album_uri=uri,
                        filename_or_handle=libpub.filename)
                except Exception, e:
                    libpub.alert('Upload Failure: %s'%e)
                    libpub.destroy()
                    
                if img:
                    libpub.alert('Photo upload to Picasaweb was successful',gtk.MESSAGE_INFO)
                
                
            # Insert tag
            try:
                for tag in tags.split():
                    pws.InsertTag(img,tag)
            except Exception, e:
                libpub.alert('Failed to add tag to image: %s'%e)
                libpub.destroy()
                
            # save the current album into config file
            libpub.config.set('PICASA_LAST_ALBUM',curalbum)
            
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
            
    def picweb_login_handler(self,widget,data=None):
        self.username = self.picwebRegBox.usernameEntry.get_text()
        password = self.picwebRegBox.passwordEntry.get_text()
        try:
            self.picwebObject.login(self.username,password)
            self.upload_dialog()
            libpub.config.set('PICASA_LAST_USERNAME',self.username)
        except Exception, e:
            libpub.alert('Login error: %s'%e)
            
    def flickr_login_handler(self,widget,data=None):
        try:
            if self.flickrObject.get_authtoken():
                self.upload_dialog()
        except Exception, e:
            libpub.alert("Unhandled exception while Flickr login: %s"%e)
     
        
        
