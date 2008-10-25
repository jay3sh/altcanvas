#!/usr/bin/env python

import sys
import traceback
sys.path.append('/var/www/html')
from flickr import getDesktopFlickr
import logging

def getAltCanvasXmlRpc():
    try:
        acxr = AltCanvasXmlRpc()
    except AltCanvasXmlRpc, acxrE:
        acxr = acxrE
    return acxr

class AltCanvasXmlRpc:
    __single = None
    def __init__(self):
        if self.__single:
            raise self.__single
        self.__single = self
        self.flickr = getDesktopFlickr()

    def getFrob(self,meta):
        logging.debug("XMLRPC: getFrob")
        frob = self.flickr.auth_getFrob()
        return frob
    
    def getAuthUrl(self,meta,*args):
        logging.debug("XMLRPC: getAuthUrl")
        if len(args) <= 0:
            return None
        frob = args[0]
        url = self.flickr.getFlickrAuthURL(frob=frob)
        if url == None or len(url) <= 0:
            logging.error("Error getting Auth URL")
            return None
        else:
            return url[0]
    
    def getAuthToken(self,meta,*args):
        logging.debug("XMLRPC: getAuthToken")
        if len(args) <= 0:
            return None
        frob = args[0]
        userinfo = self.flickr.auth_getToken(frob=frob)
        if userinfo == None:
            logging.error("Couldn't retrieve authtoken")
            return None
        else:
            return userinfo.token
    
    def signParams(self,meta,*args):
        logging.debug("XMLRPC: signParams")
        signedargs = self.flickr.process_args(args[0])
        return signedargs
    
    def setLicense(self,meta,*args):
        logging.debug("XMLRPC: setLicense")
        try:
            if len(args) < 3:
                return None
            authtoken = args[0]
            imageID = args[1]
            licenseID = args[2]
            self.flickr.photos_licenses_setLicense(
                photo_id=imageID,
                license_id=licenseID,
                auth_token=authtoken)
        except Exception, e:
            logging.error('Exception setLicense: %s'%e)
        
    def getImageUrl(self,meta,*args):
        logging.debug("XMLRPC: getImageUrl")
        try:
            if len(args) < 2:
                return None
            authtoken = args[0]
            imageID = args[1]
            if imageID != None:
                logging.debug('GIMP image upload: %s'%imageID)
                info = self.flickr.photos_getInfo(auth_token=authtoken,photo_id=imageID)
                if info == None:
                    return None
                url = info.urls[0].url[0].elementText
                return url
            else:
                return None
        except Exception, e:
            logging.error('Exception getUrl: %s'%e)
            return None

    def getPhotoSets(self,meta,*args):
        logging.debug("XMLRPC: getPhotoSets")
        try:
            if len(args) <= 0:
                return None
            
            authtoken = args[0]
            userInfo = self.flickr.auth_checkToken(auth_token=authtoken)
            photosets = self.flickr.photosets_getList(user_id=userInfo.nsid)
            return photosets
        except Exception, e:
            for line in traceback.format_exc().split('\n'):
                logging.error(line)
            return None
        
    def createPhotoSet(self,meta,*args):
        logging.debug("XMLRPC: createPhotoSet")
        try:
            if len(args) < 3:
                return None
            authtoken = args[0]
            imageID = args[1]
            title = args[2]
            
            photosetID = self.flickr.photosets_create(
                title=title,primary_photo_id=imageID,auth_token=authtoken)
            
            return photosetID
        except Exception, e:
            for line in traceback.format_exc().split('\n'):
                logging.error(line)
            return None
    
    def deletePhotoSet(self,meta,*args):
        logging.debug("XMLRPC: deletePhotoSet")
        try:
            if len(args) < 2:
                return None
            authtoken = args[0]
            setID = args[1]
            
            respstr = self.flickr.photosets_delete(
                        auth_token=authtoken,photoset_id=setID)
            return True
        except Exception, e:
            for line in traceback.format_exc().split('\n'):
                logging.error(line)
            return False
            
    def addPhoto2Set(self,meta,*args):
        logging.debug("XMLRPC: addPhoto2Set")
        try:
            if len(args) < 3:
                return False
            authtoken = args[0]
            photo_id = args[1]
            set_id = args[2]
            respstr = self.flickr.photosets_addPhoto(
                        auth_token=authtoken,photoset_id=set_id,photo_id=photo_id)
            return True
        except Exception, e:
            for line in traceback.format_exc().split('\n'):
                logging.error(line)
            return False
            
    def reportPublishrCrash(self,meta,*args):
        logging.debug("XMLRPC: reportCrash")
        try:
            if len(args) < 1:
                return 
            #TODO
            crash_report = args[0]
            logging.error('CRASH REPORT:'+crash_report)
        except Exception, e:
            for line in traceback.format_exc().split('\n'):
                logging.error(line)
            return False
            

