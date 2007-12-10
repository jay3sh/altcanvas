#!/usr/bin/env python

import xmlrpclib
import unittest
import sys
import os
import time
sys.path.append(os.getcwd()+'/..')
from libpub.flickr import Flickr

SERVER='http://www.altcanvas.com/xmlrpc/'

# global data
authtoken = None
imageID = None

class LoginTests(unittest.TestCase):
    def setUp(self):
        self.keyserver = xmlrpclib.Server(SERVER)
        self.frob = self.keyserver.altcanvas.getFrob()
        authurl = self.keyserver.altcanvas.getAuthUrl(self.frob)
        os.system("%s '%s'" % ('firefox', authurl))
        time.sleep(3)
        
    def testAuthToken(self):
        global authtoken
        authtoken = self.keyserver.altcanvas.getAuthToken(self.frob)
        self.assertNotEquals(authtoken,None)
        
class UploadTests(unittest.TestCase):
    def setUp(self):
        self.keyserver = xmlrpclib.Server(SERVER)
        
    def testUpload(self):
    	global imageID
    	global authtoken
        self.f = Flickr(self.keyserver)
        imageID = self.f.upload(
                filename='/tmp/test123.jpg',
                title='test title',
                auth_token=authtoken,
                is_public='0',    
                tags='testing',
                description='testing desc')
        self.assert_(imageID)
        
class CreateDeletePhotosetTests(unittest.TestCase):
    def setUp(self):
        self.keyserver = xmlrpclib.Server(SERVER)
        
    def testCreateDeletePhotoset(self):
        global authtoken
    	global imageID
    	setID = self.keyserver.altcanvas.createPhotoSet(authtoken,imageID,'testset')
    	self.assert_(setID)
    	
    	result = self.keyserver.altcanvas.deletePhotoSet(authtoken,setID)
    	self.assert_(result)
	
        
class DataTests(unittest.TestCase):
    def setUp(self):
        self.keyserver = xmlrpclib.Server(SERVER)
        
    def testImageUrl(self):
        imageurl = self.keyserver.altcanvas.getImageUrl('1962946544')
        self.assert_(imageurl,'http://www.flickr.com/photos/jyro/1962946544/')
        
    def testPhotoSets(self):
        global authtoken
        global imageID
        self.photosets = self.keyserver.altcanvas.getPhotoSets(authtoken)
        self.assert_(self.photosets)
        titles = []
        target_set_id = None
        for photoset in self.photosets:
            if photoset['title'] == 'set_one':
                target_set_id = photoset['id']
            titles.append(photoset['title'])
        self.assert_('set_one' in titles)
        self.assert_(target_set_id)
        result = self.keyserver.altcanvas.addPhoto2Set(authtoken,imageID,target_set_id)
        self.assert_(result)
        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(LoginTests)
    loginTestResult = unittest.TextTestRunner(verbosity=2).run(suite)
    
    if not loginTestResult.wasSuccessful():
        sys.exit()
        
    suite = unittest.TestLoader().loadTestsFromTestCase(UploadTests)
    uploadTestResult = unittest.TextTestRunner(verbosity=2).run(suite)
        
    if not uploadTestResult.wasSuccessful():
        sys.exit()
        
    suite = unittest.TestLoader().loadTestsFromTestCase(CreateDeletePhotosetTests)
    dataTestResult = unittest.TextTestRunner(verbosity=2).run(suite)
