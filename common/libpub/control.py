import libpub
import libpub.gui

class Control:
    def __init__(self,window):
        self.window = window
    
    def entry(self):
        entry = libpub.gui.Entry(flickr_handler=self.flickr_entry_handler,
              picasa_handler=self.picasa_entry_handler)
        self.window.add(entry)
        
    def flickr_entry_handler(self,widget,data=None):
        import libpub.flickr
        self.empty_window()
        
        self.flickr = libpub.flickr.FlickrObject()
        self.apptype = 'FLICKR'
        
        # If authtoken is found locally, directly go to Upload dialog
        if self.flickr.has_auth():
            uploadDlg = libpub.gui.UploadDlg(apptype='FLICKR',
                            flickrObject=self.flickr,
                            upload_handler=self.upload)
            self.window.add(uploadDlg)
        else:
            flickrRegBox = libpub.gui.FlickrRegistrationBox(flickr = self.flickr,
                                login_handler = self.flickr_login_handler)
            self.window.add(flickrRegBox)
    
    def picasa_entry_handler(self,widget,data=None):
        import libpub.picasa
        self.empty_window()
        
        self.picasa = libpub.picasa.PicasawebObject()
        self.apptype = 'PICASAWEB'
        self.picwebRegBox = libpub.gui.PicasawebRegisterBox(
                                login_handler=self.picasa_login_handler)
        self.window.add(self.picwebRegBox)
        
    def flickr_login_handler(self,widget,data=None):
        self.empty_window()
        if self.flickr.get_authtoken():
            uploadDlg = libpub.gui.UploadDlg(apptype='FLICKR',
                            serviceObject=self.flickr,
                            upload_handler=self.upload)
            self.window.add(uploadDlg)
        
    def picasa_login_handler(self,widget,data=None):
        self.empty_window()
        try:
            username = self.picwebRegBox.usernameEntry.get_text()
            password = self.picwebRegBox.passwordEntry.get_text()
            self.picasa.login(username,password)
            
            uploadDlg = libpub.gui.UploadDlg(apptype='PICASAWEB',
                            serviceObject=self.picasa,
                            upload_handler=self.upload)
            self.window.add(uploadDlg)
        
            if self.picwebRegBox.remember_check.get_active():
                libpub.conf.set('PICASA_LAST_USERNAME',username)
            else:
                libpub.conf.set('PICASA_LAST_USERNAME',None)
            
        except Exception, e:
            libpub.alert('Login error: %s'%e)
    
    def upload(self,widget,data=None):
        pass

    def empty_window(self):
        for box in self.window.get_children():
            self.window.remove(box)
