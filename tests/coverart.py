#!/usr/bin/env python


from libpub.utils.xmlparser import XMLNode
import sys
import urllib


def query(url):
    instream = urllib.urlopen(url)

    xmlresp = ""
    for line in instream.readlines():
        xmlresp += line

    print xmlresp
    print "-"*100
    
    return xmlresp


def getItem(ASIN):
    url = "http://ecs.amazonaws.com/onca/xml?Service=AWSECommerceService"
    url += "&AWSAccessKeyId=0FWKGK43D4E0B7DDRK82"
    url += "&AssociateTag=devconn-20"
    url += "&Operation=ItemLookup"
    url += "&ItemId="+ASIN
    url += "&ResponseGroup=ItemAttributes,Images"

    xmlresp = query(url)

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
    searchItem(sys.argv[1:])


if __name__ == '__main__':
    main()
