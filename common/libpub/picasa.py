#
# Acknowledgement for Picasaweb code:
#    The Picasaweb code that uses Google's gdata library to access Picasaweb Album
#    is derived from manatlan's code. 
#    It can be found at:
#    http://jbrout.python-hosting.com/file/trunk/plugins/multiexport/libs/picasaweb/__init__.py?rev=193
#

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

class PicasaWeb(libpub.gdata.service.GDataService):
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
        
        
class PicasawebObject:
    picweb=None
    def __init__(self):
        self.picweb = libpub.gdata.photos.service.PhotosService()
    
    def login(self,username,password):
        self.picweb.ClientLogin(username,password)
    
class PicasawebRegisterBox(gtk.VBox):
    def __init__(self,parent):
        gtk.VBox.__init__(self)
        self.picwebObject = parent.picwebObject
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
        self.loginButton.connect("clicked",parent.picweb_login_handler)
        self.cancelButton = gtk.Button('Cancel')
        self.cancelButton.connect("clicked",libpub.destroy)
        
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
        
        # Recall last settings, if available
        last_username = libpub.config.get('PICASA_LAST_USERNAME')
        if last_username:
            self.usernameEntry.set_text(last_username)
            self.usernameEntry.grab_focus()
        
        self.show_all()
        
