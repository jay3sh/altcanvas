
import gtk

import libpub

if libpub.HOSTAPP == 'Maemo':
    import libpub.maemo_gui as gui
else:
    import libpub.gui as gui

class Control:
    def __init__(self,window):
        self.window = window
    
    def entry(self):
        entry = gui.Entry(flickr_handler=self.flickr_entry_handler,
              picasa_handler=self.picasa_entry_handler)
        self.window.add(entry)
        
    def flickr_entry_handler(self,widget,data=None):
        import libpub.flickr
        self.empty_window()
        
        self.flickr = libpub.flickr.FlickrObject()
        self.apptype = 'FLICKR'
        
        # If authtoken is found locally, directly go to Upload dialog
        if self.flickr.has_auth():
            self.uploadDlg = gui.UploadDlg(apptype='FLICKR',
                            serviceObject=self.flickr,
                            upload_handler=self.upload)
            self.window.add(self.uploadDlg)
        else:
            self.flickrRegBox = gui.FlickrRegisterBox(flickr = self.flickr,
                                login_handler = self.flickr_login_handler)
            self.window.add(self.flickrRegBox)
    
    def picasa_entry_handler(self,widget,data=None):
        import libpub.picasa
        self.empty_window()
        
        self.picasa = libpub.picasa.PicasawebObject()
        self.apptype = 'PICASAWEB'
        self.picwebRegBox = gui.PicasawebRegisterBox(
                                login_handler=self.picasa_login_handler)
        self.window.add(self.picwebRegBox)
        
    def flickr_login_handler(self,widget,data=None):
        self.empty_window()
        if self.flickr.get_authtoken():
            self.uploadDlg = gui.UploadDlg(apptype='FLICKR',
                            serviceObject=self.flickr,
                            upload_handler=self.upload)
            self.window.add(self.uploadDlg)
        else:
            self.window.add(self.flickrRegBox)
        
    def picasa_login_handler(self,widget,data=None):
        self.empty_window()
        try:
            username = self.picwebRegBox.usernameEntry.get_text()
            password = self.picwebRegBox.passwordEntry.get_text()
            self.picasa.login(username,password)
            
            self.uploadDlg = gui.UploadDlg(apptype='PICASAWEB',
                            serviceObject=self.picasa,
                            upload_handler=self.upload)
            self.window.add(self.uploadDlg)
        
            if self.picwebRegBox.remember_check.get_active():
                libpub.conf.set('PICASA_LAST_USERNAME',username)
            else:
                libpub.conf.set('PICASA_LAST_USERNAME',None)
            
        except Exception, e:
            libpub.alert('Login error: %s'%e)
            self.window.add(self.picwebRegBox)
    
    def upload(self,widget,data=None):
        self.title = self.uploadDlg.titleEntry.get_text()
        buffer = self.uploadDlg.descView.get_buffer()
        startiter,enditer = buffer.get_bounds()
        desc = buffer.get_text(startiter,enditer)
        tags = self.uploadDlg.tagEntry.get_text()
        
        # Get the index of chosen license 
        license_index = self.uploadDlg.licenseCombo.get_active()
            
        # Get the chosen album name
        model = self.uploadDlg.albumCombo.get_model()
        active = self.uploadDlg.albumCombo.get_active()
        if active < 0:
            curalbum = self.uploadDlg.albumCombo.get_active_text()
        else:
            curalbum = model[active][0]
            
        # Upload to Flickr
        if self.apptype == 'FLICKR':
            
            from libpub.flickr import FlickrException
            
            # Get license ID for chosen license
            if license_index > 0 and license_index < len(libpub.LicenseList):
                license_id = libpub.LicenseList[license_index][0]
            else:
                license_id = 0
                
            try:
                # Upload the photo
                url = self.flickr.upload(
                        filename = libpub.filename,
                        title = self.title,
                        description = desc,
                        is_public = self.uploadDlg.is_public,
                        tags = tags,
                        license_id = str(license_id),
                        photoset = curalbum)
                
                if url:
                    # save the current album into config file
                    libpub.conf.set('FLICKR_LAST_PHOTOSET',curalbum)
                    libpub.conf.set('LAST_PRIVACY_CHOICE',self.uploadDlg.is_public)
                    libpub.conf.set('LAST_LICENSE_USED',license_index)
            
                    # success message
                    libpub.alert("Image upload was successful.\n(Flickr URL: %s)"%url,
                             gtk.MESSAGE_INFO)
                
            except FlickrException, fe:
                libpub.alert("Flickr Exception: %s"%fe)
                
            except Exception, e:
                libpub.alert("Upload exception: %s"%e)
                
            
        # Upload to Picasaweb
        elif self.apptype == 'PICASAWEB':
                
            from libpub.gdata.photos.service import PicasaException
            success = False
            
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
                success = self.picasa.upload(
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
                libpub.conf.set('PICASA_LAST_ALBUM',curalbum)
            	libpub.conf.set('LAST_LICENSE_USED',license_index)
                libpub.alert('Successful upload to Picasaweb!',gtk.MESSAGE_INFO)
            
        # Cleanup the GUI
        libpub.destroy()

    def empty_window(self):
        for box in self.window.get_children():
            self.window.remove(box)
