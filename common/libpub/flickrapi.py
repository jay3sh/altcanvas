# Copyright (c) 2007 by the respective coders, see
# http://flickrapi.sf.net/
# http://www.altcanvas.com
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import os
import sys
import urllib
import urllib2
import md5
import mimetools
#from mod_python import apache
import traceback


'''FlickrAPI uses its own in-memory XML representation, to be able to easily
use the info returned from Flickr.

There is no need to use this module directly, you'll get XMLNode instances
from the FlickrAPI method calls.
'''

import xml.dom.minidom
import libpub

__all__ = ('XMLNode', )

class XMLNode:
    """XMLNode -- generic class for holding an XML node

    xml_str = '''<xml foo="32">
    <name bar="10">Name0</name>
    <name bar="11" baz="12">Name1</name>
    </xml>'''

    f = XMLNode.parseXML(xml_str)

    print f.elementName              # xml
    print f['foo']                   # 32
    print f.name                     # [<name XMLNode>, <name XMLNode>]
    print f.name[0].elementName      # name
    print f.name[0]["bar"]           # 10
    print f.name[0].elementText      # Name0
    print f.name[1].elementName      # name
    print f.name[1]["bar"]           # 11
    print f.name[1]["baz"]           # 12

    """

    def __init__(self):
        """Construct an empty XML node."""
        self.elementName = ""
        self.elementText = ""
        self.attrib = {}
        self.xml = ""

    def __setitem__(self, key, item):
        """Store a node's attribute in the attrib hash."""
        self.attrib[key] = item

    def __getitem__(self, key):
        """Retrieve a node's attribute from the attrib hash."""
        return self.attrib[key]

    #-----------------------------------------------------------------------
    @classmethod
    def parseXML(cls, xml_str, store_xml=False):
        """Convert an XML string into a nice instance tree of XMLNodes.

        xml_str -- the XML to parse
        store_xml -- if True, stores the XML string in the root XMLNode.xml

        """

        def __parseXMLElement(element, thisNode):
            """Recursive call to process this XMLNode."""
            thisNode.elementName = element.nodeName

            #print element.nodeName

            # add element attributes as attributes to this node
            for i in range(element.attributes.length):
                an = element.attributes.item(i)
                thisNode[an.name] = an.nodeValue

            for a in element.childNodes:
                if a.nodeType == xml.dom.Node.ELEMENT_NODE:

                    child = XMLNode()
                    try:
                        list = getattr(thisNode, a.nodeName)
                    except AttributeError:
                        setattr(thisNode, a.nodeName, [])

                    # add the child node as an attrib to this node
                    list = getattr(thisNode, a.nodeName)
                    list.append(child)

                    __parseXMLElement(a, child)

                elif a.nodeType == xml.dom.Node.TEXT_NODE:
                    thisNode.elementText += a.nodeValue
            
            return thisNode

        dom = xml.dom.minidom.parseString(xml_str)

        # get the root
        rootNode = XMLNode()
        if store_xml: rootNode.xml = xml_str

        return __parseXMLElement(dom.firstChild, rootNode)

    
##
#
#    This tries to implement a makeshift factory pattern
#    Instead of making Flickr API object as a singleton object, it was
#    needed to have different flavors of it for web and desktop applications
#    So based on the apptype following functions create corresponding objects.
#    However they are singleton instances of those types.
##

class UserInfo:
    def __init__(self):
        self.token = None
        self.perms = None
        self.nsid = None
        self.username = None
        
class PhotoSet:
    def __init__(self):
        self.id = None
        self.primary = None
        self.secret = None
        self.server = None
        self.farm = None
        self.photos = None
        self.title = None
        self.desc = None

class Flickr:
    def __init__(self):

        FLICKR_APIKEY = '1e944bca11ad38e5929f4235ee7b271e'
        FLICKR_SECRET = '43d39ee73c2e1ba6'
            
        self.flickr_apikey = FLICKR_APIKEY
        self.flickr_secret = FLICKR_SECRET
            

        self.fHost = 'api.flickr.com'
        self.fRestURL = '/services/rest/'
        self.fAuthURL = '/services/auth/'
        self.fUploadURL = '/services/upload/'

    def sign(self,args):
        argkeys = args.keys()
        argkeys.sort()
        sig_str = self.flickr_secret
        for i in argkeys:
            sig_str += '%s%s'%(i,args[i])
        hash = md5.new()
        hash.update(sig_str)
        return hash.hexdigest()

    def __getattr__(self,method):
        # Refuse to act as a proxy for unimplemented special methods
        if method.startswith('__'):
            raise AttributeError("No such attribute '%s'" % method)

        method = 'flickr.' + method.replace('_','.')

        def handler(**args):
            defaults = {'method':method,
                        'api_key':self.flickr_apikey}

            self.fURL = 'http://'+self.fHost+self.fRestURL

            for key, default_value in defaults.iteritems():
                if key not in args:
                    args[key] = default_value
                if key in args and args[key] is None:
                    del args[key]

            api_sig = self.sign(args)
            postData = urllib.urlencode(args)+'&api_sig='+api_sig
            f = urllib.urlopen(self.fURL,postData)
            data = f.read()
            f.close()

            result = self.testResult(data)
                
            if method == 'flickr.auth.getFrob':
                if result != None:
                    return result.frob[0].elementText

            elif method == 'flickr.auth.getToken' or method == 'flickr.auth.checkToken':
                if result != None:
                    userInfo = UserInfo()
                    userInfo.token = result.auth[0].token[0].elementText
                    userInfo.perms = result.auth[0].perms[0].elementText    
                    userInfo.nsid = result.auth[0].user[0]['nsid']
                    userInfo.username = result.auth[0].user[0]['username']
                    return userInfo

            elif method == 'flickr.people.findByUsername':
                if result != None:
                    userInfo = UserInfo()
                    userInfo.nsid = result.user[0]['nsid']
                    userInfo.username = result.user[0].username[0].elementText
                    return userInfo

            elif method == 'flickr.photos.search':
                if result != None:
                    return result.photos[0]

            elif method == 'flickr.people.getPublicPhotos':
                if result != None:
                    return result.photos[0]

            elif method == 'flickr.photos.getFavorites':
                if result != None:
                    return result.photo[0]['total']

            elif method == 'flickr.favorites.getList':
                if result != None:
                    return result.photos[0]

            elif method == 'flickr.photos.getInfo':
                if result != None:
                    return result.photo[0]

            elif method == 'flickr.photos.getSizes':
                if result != None:
                    return result.sizes[0]
                
            elif method == 'flickr.photosets.getList':
                if result != None:
                    photosets = []
                    sets = result.photosets[0].photoset
                    for set in sets:
                        photoset = PhotoSet()
                        photoset.id = set['id']
                        photoset.primary = set['primary']
                        photoset.secret = set['secret']
                        photoset.farm = set['farm']
                        photoset.server = set['server']
                        photoset.photos = set['photos']
                        photoset.title = set.title[0].elementText
                        photoset.desc = set.description[0].elementText
                        photosets.append(photoset)
                    return photosets
            elif method == 'flickr.photosets.create':
                if result != None:
                    return result.photoset[0]['id']
            else:
                return data

            return None    # When calls fail this is returned
            
        return handler     # __getattr__ return

    def testResult(self,data):
        try:
            result = XMLNode.parseXML(data)
        except Exception, e:
            print(
                '[ERROR] Flickr API (XML parsing error): (%s) %s'%(e,data))
            return None

        if result['stat'] != 'ok':
            libpub.alert('[ERROR] Flickr API call failed: %s'%(data))
            return None
        else:
            return result
        
    def process_args(self,arg):
        # verify key names
        possible_args = ("api_key", "auth_token", "title", 
                                "description", "tags",
                                "is_public", "is_friend", "is_family")
        for a in arg.keys():
            if a not in possible_args:
                raise IllegalArgumentException("Unknown arg")

        # Set some defaults
        defaults = {'api_key': self.flickr_apikey}
        for key, default_value in defaults.iteritems():
            if key not in arg:
                arg[key] = default_value
            if key in arg and arg[key] is None:
                del arg[key]
                
        arg["api_sig"] = self.sign(arg)
        return arg


    def upload(self, filename=None, jpegData=None, **arg):
        """Upload a file to flickr.

        Supported parameters:
        One of filename or jpegData must be specified by name when 
        calling this method:

        filename -- name of a file to upload
        jpegData -- array of jpeg data to upload

        title
        description
        tags -- space-delimited list of tags, "tag1 tag2 tag3"
        is_public -- "1" or "0"
        is_friend -- "1" or "0"
        is_family -- "1" or "0"
        """

        if filename == None and jpegData == None or \
            filename != None and jpegData != None:
            raise IllegalArgumentException(
                    "filename OR jpegData must be specified")

        arg = self.process_args(arg)

        url = "http://" + self.fHost + self.fUploadURL

        # construct POST data
        boundary = mimetools.choose_boundary()
        body = ""

        # required params
        for a in ('api_key', 'auth_token', 'api_sig'):
            body += "--%s\r\n" % (boundary)
            body += "Content-Disposition: form-data; name=\""+a+"\"\r\n\r\n"
            body += "%s\r\n" % (arg[a])

        # optional params
        for a in ('title', 'description', 'tags', 'is_public', \
            'is_friend', 'is_family'):

            if arg.has_key(a):
                body += "--%s\r\n" % (boundary)
                body += "Content-Disposition: form-data; name=\""+a+"\"\r\n\r\n"
                body += "%s\r\n" % (arg[a])

        body += "--%s\r\n" % (boundary)
        body += "Content-Disposition: form-data; name=\"photo\";"
        body += " filename=\"%s\"\r\n" % filename
        body += "Content-Type: image/jpeg\r\n\r\n"

        if filename != None:
            fp = file(filename, "rb")
            data = fp.read()
            fp.close()
        else:
            data = jpegData

        postData = body.encode("utf_8") + data + \
            ("\r\n--%s--" % (boundary)).encode("utf_8")

        request = urllib2.Request(url)
        request.add_data(postData)
        request.add_header("Content-Type", \
            "multipart/form-data; boundary=%s" % boundary)
        response = urllib2.urlopen(request)
        rspXML = response.read()

        result = XMLNode.parseXML(rspXML)
        
        if result != None:
            id = result.photoid[0].elementText
            return id
        else:
            return None

    def getFlickrAuthURL(self,frob=None):
        self.app = 'desktop'
        if self.app == 'web':
            s = '%s%s%s%s%s'%(
                self.flickr_secret,'api_key',
                self.flickr_apikey,'perms','write')
            md5_hash = md5.new()
            md5_hash.update(s)
            api_sig = md5_hash.hexdigest()
            furl = '%s%s%s%s'%(
                'http://www.flickr.com/services/auth/?api_key=',
                self.flickr_apikey,
                '&perms=write&api_sig=',api_sig)
            return (furl,)
        elif self.app == 'desktop':
            if frob == None:
                return None
            s = '%s%s%s%s%s%s%s'%(
                self.flickr_secret,
                'api_key',self.flickr_apikey,
                'frob',frob,
                'perms','write')
            md5_hash = md5.new()
            md5_hash.update(s)
            api_sig = md5_hash.hexdigest()
            furl = '%s%s%s%s%s%s'%(
                'http://www.flickr.com/services/auth/?api_key=',
                self.flickr_apikey,
                '&perms=write&frob=',frob,'&api_sig=',api_sig)
            return (furl,)
        else:
            raise Exception('Impossible case')
            


if __name__ == '__main__':
    f = Flickr()

    #u = f.people_findByUsername(username=sys.argv[1])
    #print u.username

    #photos = f.photos_search(license='1',per_page='10')
    #for p in photos.photo:
    #    print p['id']

    #photos = f.photos_search(license='1',per_page='28',text=sys.argv[1])
    #for p in photos.photo:
    #    print p['id'],p['title']

    #f.upload(filename=sys.argv[1],title='lal-kila-2233',
    #    auth_token='xxxxxxxxxxx',
    #    is_public='1',tags='altcanvas travel delhi history india',
    #    description='historic place in India capital')

    #f.photos_licenses_setLicense(photo_id='1567154282',license_id='1',auth_token='xxxxxxxxxx')
