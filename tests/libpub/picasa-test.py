
import unittest
import sys
import os
import traceback
import getpass

import libpub.gdata.photos.service


class PicasaTest(unittest.TestCase):
    def setUp(self):
        global username
        global password
        self.pws = libpub.gdata.photos.service.PhotosService()
        if sys.platform.find('win32') >= 0:
            self.filename = 'C:\\Documents and Settings\\jayesh\\Desktop\\publishr-folder\\test2.jpg'
        else:
            self.filename = '/tmp/test123.jpg'
        self.pws.ClientLogin(username,password)
        
    def testAlbum(self):
        albums = self.pws.GetUserFeed().entry
        
        for a in albums:
            if a.title.text == 'gumstix':
                return
        self.fail('Failed to find expected album')
        
    def testAlbumCD(self):
        test_album = self.pws.InsertAlbum('test_album_123','test')
        self.pws.Delete(test_album)
        
            
    def testImageUpload(self):
        albums = self.pws.GetUserFeed().entry
        
        for a in albums:
            if a.title.text == 'Gimp':
                try:
                    image_entry = self.client.InsertPhotoSimple(a,
                   	'title145', 'a pretty testing picture', self.filename)
                    self.assert_(image_entry.title.text == 'title145')
                    results_feed = self.client.SearchUserPhotos('title145')
                    self.assert_(len(results_feed.entry) > 0)
                    self.client.Delete(image_entry)
                    
                except Exception, e:
                     for line in traceback.format_exc().split('\n'):
                         print line
                     self.fail('Photo insert-delete failed: %s'%e)
                    

if __name__ == '__main__':
    username = raw_input('Please enter your username: ')
    password = getpass.getpass()
    
    suite = unittest.TestLoader().loadTestsFromTestCase(PicasaTest)
    picasaTestResult = unittest.TextTestRunner(verbosity=2).run(suite)
