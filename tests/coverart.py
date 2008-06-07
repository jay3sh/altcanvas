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

        for keyword in keywords:
            kw_str = keyword+"%20"
        params['Keywords'] = kw_str

        url = self.__generate_url(params)

        xmlresp = self.__query(url)
        
        resp = XMLNode().parseXML(xmlresp)

        asin_list = []
        for item in resp.Items[0].Item:
            asin_list.append(item.ASIN[0].elementText)

        return asin_list

    def getDetail(self,id):
        pass




def getItem(ASIN):
    url = "http://ecs.amazonaws.com/onca/xml?Service=AWSECommerceService"
    url += "&AWSAccessKeyId=0FWKGK43D4E0B7DDRK82"
    url += "&AssociateTag=devconn-20"
    url += "&Operation=ItemLookup"
    url += "&ItemId="+ASIN
    url += "&ResponseGroup=ItemAttributes,Images"

    xmlresp = query(url)

    print xmlresp

    resp = XMLNode().parseXML(xmlresp)
    print resp.Items[0].Item[0].ImageSets[0].ImageSet[0].LargeImage[0].URL[0].elementText

def searchItem(keywords):
    url = "http://ecs.amazonaws.com/onca/xml?Service=AWSECommerceService"
    url += "&AWSAccessKeyId=0FWKGK43D4E0B7DDRK82"
    url += "&AssociateTag=devconn-20"
    url += "&Operation=ItemSearch"
    url += "&SearchIndex=Music"
    url += "&Keywords="
    for arg in keywords:
        url += arg+"%20"

    xmlresp = query(url)

    resp = XMLNode().parseXML(xmlresp)

    for item in resp.Items[0].Item:
        details = getItem(item.ASIN[0].elementText)
        
        break
        '''
        print item.ASIN[0].elementText
        if 'Artist' in dir(item.ItemAttributes[0]):
            sys.stdout.write(
                item.ItemAttributes[0].Artist[0].elementText)
        if 'Manufacturer' in dir(item.ItemAttributes[0]):
            sys.stdout.write( ' - '+
                item.ItemAttributes[0].Manufacturer[0].elementText)
        if 'Title' in dir(item.ItemAttributes[0]):
            sys.stdout.write( ' - '+
                item.ItemAttributes[0].Title[0].elementText)
        '''

def main():
    #searchItem(sys.argv[1:])
    amz = Amazon()
    print amz.search(sys.argv[1:])


if __name__ == '__main__':
    main()
