import gtk

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
        
        
        from libpub.imagic import ImageMagick
        thumbnail = None
        im = ImageMagick()
        if im.present():
            thumbname = im.makeThumbnail(libpub.filename)
            if thumbname:
                thumbgeo = im.getThumbnailGeometry(thumbname)
                thumbnail = gtk.Image()
                thumbnail.set_from_file(thumbname)

        # Pack all widgets
        serviceBox = gtk.VBox()
        serviceBox.pack_start(self.flickrButton,expand=False)
        serviceBox.pack_start(self.picwebButton,expand=False)
        serviceBox.set_spacing(5)

        empty_window()
        
        outerBox = gtk.VBox()
        if thumbnail:
            imageBox = gtk.VBox()
            imageBox.pack_start(thumbnail)
            imageBox.set_border_width(10)
            outerBox.pack_start(imageBox)
        serviceBox.set_border_width(5)
        outerBox.pack_start(serviceBox)
            
        outerBox.show_all()
        self.window.add(outerBox)
        
    def upload_dialog(self):
        # Define UI widgets
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

        okButton = gtk.Button('Upload')
        okButton.connect("clicked",self.upload)
        cancelButton = gtk.Button('Quit')
        cancelButton.connect("clicked",libpub.destroy)
        signoutButton = gtk.Button('Sign out')
        signoutButton.connect("clicked",libpub.signout)
        
        # packing widgets
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
        tagBox.set_border_width(4)

        licenseBox = gtk.HBox()
        licenseBox.pack_start(licenseLabel)
        licenseBox.pack_start(self.licenseCombo)

        inputBox = gtk.VBox()
        inputBox.pack_start(titleBox)
        inputBox.pack_start(descBox)
        inputBox.pack_start(tagBox)
        inputBox.pack_start(licenseBox)
        inputBox.set_border_width(4)

        buttonBox = gtk.HBox()
        buttonBox.pack_start(okButton)
        buttonBox.pack_start(cancelButton)
        buttonBox.pack_start(signoutButton)
        buttonBox.set_border_width(4)
        
        if self.type == 'PICASAWEB':
            signoutButton.hide()
            titleBox.hide()
            self.tagEntry.set_text('not supported yet')
            self.tagEntry.set_state(gtk.STATE_INSENSITIVE)
            self.licenseCombo.append_text('not supported yet')
            model = self.licenseCombo.get_model()
            self.licenseCombo.set_active(len(model)-1)
            self.licenseCombo.set_state(gtk.STATE_INSENSITIVE)

        uploadBox = gtk.VBox()
        uploadBox.pack_start(inputBox)
        uploadBox.pack_start(buttonBox)
        uploadBox.set_border_width(6)
        
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
            
        # Upload to Flickr
        if self.type == 'FLICKR':
            flickrObject = self.webservice
            flickrObject.connect()
            flickr = Flickr(flickrObject.keyserver)
            imageID = flickr.upload(
                    filename=libpub.filename,
                    title=title,
                    auth_token=flickrObject.authtoken,
                    is_public='1',    # TODO programmable
                    tags=tags,
                    description=desc)
        
            if imageID != None:
                url = flickrObject.keyserver.altcanvas.getImageUrl(imageID)
                libpub.alert("Image upload was successful.\n(Flickr URL: %s)"%url,
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
                </entry>'''%(libpub.filename.rpartition(os.sep)[2],desc)
            picwebObject = self.webservice
            pw = picwebObject.picweb
            albumlist = pw.getAlbums()
            img = None
            for a in albumlist:
                if a.name == 'Gimp':
                    img = a.uploadPhoto(libpub.filename,metadata)
                    if img:
                        libpub.alert('Photo upload to Picasaweb was successful',gtk.MESSAGE_INFO)
                    else:
                        libpub.alert('Upload to Picasaweb failed')
                        return
            
            # The default album 'Gimp' was not found, create one
            if not img:
                a=pw.createAlbum("Gimp")
                img = a.uploadPhoto(libpub.filename,metadata)
                if img:
                    libpub.alert('Photo upload to Picasaweb was successful',gtk.MESSAGE_INFO)
                else:
                    libpub.alert('Upload to Picasaweb failed')
                    return
                
            destroy()
            tagmetadata = '''
                <entry xmlns='http://www.w3.org/2005/Atom'>
                    <title>altcanvas</title>
                    <category scheme="http://schemas.google.com/g/2005#kind"
                        term="http://schemas.google.com/photos/2007#tag"/>
                </entry>'''
            #result = img.updatePhoto(tagmetadata)
            
    def loadFlickr(self,widget,data=None):
        self.type = 'FLICKR'
        if not self.flickrObject.has_auth():
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
            destroy()
        
    def displayFlickrLogin(self):
        try:
            empty_window()
            self.flickrRegBox = FlickrRegisterBox(self)
            self.flickrRegBox.setup()
            self.window.add(self.flickrRegBox)
        except Exception, e:
            libpub.alert("Flickr GUI: %s"%e)
            destroy()
            
    def picweb_login_handler(self,widget,data=None):
        username = self.picwebRegBox.usernameEntry.get_text()
        password = self.picwebRegBox.passwordEntry.get_text()
        try:
            self.picwebObject.login(username,password)
        except Exception, e:
            libpub.alert('Login error: %s'%e)
            
    def flickr_login_handler(self,widget,data=None):
        try:
            authtoken = self.flickrObject.get_authtoken()
            if authtoken != None:
                save_authtoken(authtoken)
            else:
                libpub.alert("There was error retrieving Flickr Authentication token.\n"+
                      "Are you sure, you have authorized this application?\n"+
                      "Try again!")
        except Exception, e:
            libpub.alert("Network error while retrieving Auth Token: %s"%e)
     
        
        
