#!/usr/bin/env python

import S3
import time
import sys
import mimetypes
import getopt
import os



class Config:
    map = {}
    def __init__(self):
        self.CONFIG_FILE=os.getenv('HOME')+'/.S3config'
        config_f = open(self.CONFIG_FILE,'r')
        for line in config_f:
            key,val = line.strip().split('=')
            if key:
                self.map[key] = val

    def get(self,key):
        return self.map[key]

    def set(self,key,val):
        self.map[key] = val


# convert the bucket to lowercase for vanity domains
# the bucket name must be lowercase since DNS is case-insensitive

class AmazonS3:
    conn = None
    generator = None
    bucket = None
    
    def __init__(self,bucket):
        self.bucket = bucket
        config = Config()
        self.conn = S3.AWSAuthConnection(
                        config.get('AWS_ACCESS_KEY_ID'),
                        config.get('AWS_SECRET_ACCESS_KEY')) 
    	self.generator = S3.QueryStringAuthGenerator(
                        config.get('AWS_ACCESS_KEY_ID'),
                        config.get('AWS_SECRET_ACCESS_KEY')) 

        if bucket and bucket not in map(lambda x: x.name, self.conn.list_all_my_buckets().entries):
            print "Bucket %s not found. Creating..."%bucket
            self.conn.create_bucket(bucket)
            sys.exit(1);
        
    def delete_bucket(self,bucket):
        self.conn.delete_bucket(bucket)

    def save(self,filepath):
        filename = os.path.basename(filepath)
        file = open(filepath) 
        file_data = file.read(); 
        ext = os.path.splitext(filename)[1];
        if (ext == None)|(ext == ''):
            content_type = 'application/octet-stream'
        else:
            try: 
                content_type = mimetypes.types_map[ext]
            except KeyError:  
                content_type = 'application/octet-stream'
            
        result = self.conn.put( self.bucket, filename, S3.S3Object(file_data),
                                { 'Content-Type': content_type }).http_response.status
        if result != 200:
            print "save operation failed: %d"%result
            
        
    def delete(self,filename): 
        result = self.conn.delete(self.bucket, filename).http_response.status
        if result != 204:
            print "delete operation failed: %d"%result
        
        
    def restore(self,filepath):
        filename = os.path.basename(filepath) 
        file_data = self.conn.get(self.bucket,filename).object.data 
        file = open(filepath,"w"); 
        file.write(file_data); 
        file.close();
        
    def listall(self): 
        for bucket in self.conn.list_all_my_buckets().entries:
            print "%s"%bucket.name

    def list(self): 
        for file in map(lambda x: x.key, self.conn.list_bucket(self.bucket).entries):
            print "%s"%file


def usage():
    print "AmazonS3.py [option] [filename]"
    print "Bucket operations:"
    print "        -h --help    this help"
    print "        -b --bucket  bucket-name "
    print "        -D --deleteb Delete the bucket"
    print "        -a --listall list all buckets"
    print "File operations:"
    print "        -s --save    file-name    Save the file to bucket"
    print "        -d --delete  file-name    Delete the file from bucket"
    print "        -r --restore file-name    Restore the file from bucket"
    print "        -l --list    list the files stored in given bucket"
    

def main():
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hs:r:b:d:laD", 
                        ["help","save=","restore=","bucket=","delete=","list","listall"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
        
    savefile = None
    restorefile = None
    deletefile =  None
    bucket = None
    op = None

    if not opts:
        usage()
        sys.exit(0)
    
    for o,a in opts: 
        if o in ("-h","--help"):
            usage()
            sys.exit()
        if o in ("-s","--save"):
            savefile = a
            op = "save"
        if o in ("-r","--restore"):
            restorefile = a
            op = "restore"
        if o in ("-b","--bucket"):
            bucket = a
        if o in ("-D","--deleteb"):
            op = "deleteb"
        if o in ("-l","--list"):
            op = "list"
        if o in ("-d","--delete"):
            deletefile = a
            op = "delete"
        if o in ("-a","--listall"):
            op = "listall"

    if bucket != None:
        amazonS3 = AmazonS3(bucket)
    else:
        amazonS3 = AmazonS3(None)

    if op == "listall":
        amazonS3.listall()
        sys.exit()

    if op == "deleteb" and bucket != None:
        amazonS3.delete_bucket(bucket)
    
    if op == "save" and savefile != None:
        amazonS3.save(savefile)
        sys.exit()
        
    if op == "list":
        amazonS3.list()
        sys.exit()
        
    if op == "delete" and  deletefile != None:
        amazonS3.delete(deletefile)
        sys.exit()
        
    if op == "restore" and restorefile != None:
        amazonS3.restore(restorefile)
        sys.exit()

if __name__ == "__main__":
    main()
		
