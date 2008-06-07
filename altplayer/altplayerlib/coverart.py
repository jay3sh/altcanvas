#!/usr/bin/env python


from libpub.utils.xmlparser import XMLNode
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

def main():
    amz = Amazon()
    print sys.argv[1:]
    for result in amz.search(sys.argv[1:]):
        print amz.getImages(result)

        


if __name__ == '__main__':
    main()
