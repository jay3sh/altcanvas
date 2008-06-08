#!/usr/bin/env python


from altplayerlib.utils import XMLNode
import sys
import urllib

class Amazon:
    SERVICE_URL="http://ecs.amazonaws.com/onca/xml"
    SERVICE_NAME="AWSECommerceService"
    AWS_ACCESS_KEY="0FWKGK43D4E0B7DDRK82"
    def __init__(self):
        pass

    def __query(self,url):
        instream = urllib.urlopen(url)
        xmlresp = ""
        for line in instream.readlines():
            xmlresp += line
        return xmlresp
        
    def __generate_url(self,params):
        url = self.SERVICE_URL
        params['Service'] = self.SERVICE_NAME
        params['AWSAccessKeyId'] = self.AWS_ACCESS_KEY

        if len(params.items()) > 0:
            url += "?"

        for param in params.items():
            url += "%s=%s&"%param

        return url

    def search(self,keywords):
        if len(keywords) <= 0:
            return
        params = {}
        params['AssociateTag'] = 'devconn-20'
        params['Operation'] = 'ItemSearch'
        params['SearchIndex'] = 'Music'

        kw_str = ''
        for keyword in keywords:
            kw_str += keyword+"%20"
        params['Keywords'] = kw_str

        url = self.__generate_url(params)

        xmlresp = self.__query(url)
        
        try:
            resp = XMLNode().parseXML(xmlresp)
        except Exception,e:
            # XML parsing error
            print 'XML parsing error'
            return None

        # If no results are found
        if 'Item' not in dir(resp.Items[0]):
            return None

        asin_list = []
        for item in resp.Items[0].Item:
            asin_list.append(item.ASIN[0].elementText)

        return asin_list

    def getImages(self,id):
        if not id:
            return
        params = {}
        params['AssociateTag'] = 'devconn-20'
        params['Operation'] = 'ItemLookup'
        params['ItemId'] = id
        params['ResponseGroup'] = 'ItemAttributes,Images'

        url = self.__generate_url(params)
        xmlresp = self.__query(url)

        try:
            resp = XMLNode().parseXML(xmlresp)
        except Exception,e:
            # XML parsing error
            print 'XML parsing error'
            return None

        if 'ImageSets' not in dir(resp.Items[0].Item[0]):
            # No images are returned for this product ASIN
            return []

        imageSets = resp.Items[0].Item[0].ImageSets

        if not imageSets:
            return None

        images = []
        images.append(
            imageSets[0].ImageSet[0].LargeImage[0].URL[0].elementText)

        return images

'''
    Music scanning and cover art download logic
'''
import os
import traceback

from altplayerlib.id3reader import Reader as id3Reader
from altplayerlib.utils import unique

trivial_keywords = ('to','of','the')

def filter_trivial_kw(kw):
    for tkw in trivial_keywords:
        if tkw in kw:
            kw.remove(tkw)
    return kw

def normalize(string):
    string = string.lower().strip()
    string = string.replace('unknown','')
    string = string.replace(' ','%20')
    return string

def scan_music(path):
    amazon = Amazon()

    success_count = 0
    total_count = 0
    for root,dir,files in os.walk(path):
        for mp3 in files:
            try:
                print mp3
                if not mp3.lower().endswith('mp3'):
                    continue 

                total_count += 1

                id3 = id3Reader(os.path.join(root,mp3))

                tt2,tpe1,talb,performer,album,title = ( 
                    id3.getValue('TIT2'),
                    id3.getValue('TPE1'),
                    id3.getValue('TALB'),
                    id3.getValue('performer'),
                    id3.getValue('album'),
                    id3.getValue('title')
                )

                keywords = []
                print 'Tags: %s-%s-%s-%s-%s-%s'%(
                    album,performer,title,tt2,tpe1,talb)

                #
                # Use relevant id3 tags first
                for tag in (album,performer,title):
                    if tag:
                        keywords.append(normalize(tag))

                #
                # Derive keywords from the filename
                if len(keywords) == 0:
                    songname = mp3.lower().rpartition('.')[0]
                    songinfo = songname.split('-')
                    for part in songinfo:
                        keywords.append(normalize(part))

                #
                # Lastly try miscellaneous id3 tags
                if len(keywords) == 0:
                    for tag in (tt2,tpe1,talb):
                        if tag:
                            keywords.append(normalize(tag))

                keywords = unique(keywords)
                keywords = filter_trivial_kw(keywords)

                print 'Flat: '+str(keywords)

                while len(keywords) > 0:
                    results = amazon.search(keywords)

                    # If search fails try with fewer keywords
                    if not results or len(results) <= 0:
                        keywords = keywords[:-1]
                        continue

                    images = amazon.getImages(results[0])

                    # If getImage fails try with fewer keywords
                    if not images:
                        keywords = keywords[:-1]
                        continue

                    success_count += 1
                    print 'Success: '+str(keywords)
                    print " "*10+" --> "+images[0]
                    break

            except Exception, e:
                for line in traceback.format_exc().split('\n'):
                    print line

    print 'Success ratio: %d/%d'%(success_count,total_count)

    


