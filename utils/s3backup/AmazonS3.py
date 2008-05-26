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
            print "Bucket %s not found"%bucket
            print map(lambda x: x.name, self.conn.list_all_my_buckets().entries)
            sys.exit(1);
        
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
        print "All your buckets:"
        print "-----------------"
        for bucket in self.conn.list_all_my_buckets().entries:
            print "- %s"%bucket.name

    def list(self): 
        print "%s"%self.bucket
        print "========"
        for file in map(lambda x: x.key, self.conn.list_bucket(self.bucket).entries):
            print "   %s"%file


def usage():
    print "s3backup [option] [filename]"
    print "        -h --help    this help"
    print "        -b --bucket  bucket name [default read from config file]"
    print "        -s --save    save the file to S3 storage"
    print "        -d --delete  delete the file from S3 storage"
    print "        -r --restore restore the file from S3 storage"
    print "        -l --list    list the files stored in given bucket"
    print "        -a --listall list all buckets"
    

def main():
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hs:r:b:d:la", 
                        ["help","save=","restore=","bucket=","delete=","list","listall"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
        
    savefile = None
    restorefile = None
    deletefile =  None
    oplist = None
    oplistall = None
    bucket = None
    
    for o,a in opts: 
        if o in ("-h","--help"):
            usage()
            sys.exit()
        if o in ("-s","--save"):
            savefile = a
        if o in ("-r","--restore"):
            restorefile = a
        if o in ("-b","--bucket"):
            bucket = a
        if o in ("-l","--list"):
            oplist = True
        if o in ("-d","--delete"):
            deletefile = a
        if o in ("-a","--listall"):
            oplistall = True

    if oplistall == True:
        amazonS3 = AmazonS3(None)
        amazonS3.listall()
        sys.exit()
    
    if bucket != None:
        amazonS3 = AmazonS3(bucket)
    else:
        #TODO: read from config file
        sys.exit(1)
        
    if savefile != None:
        amazonS3.save(savefile)
        sys.exit()
        
    if oplist == True:
        amazonS3.list()
        sys.exit()

        
    if deletefile != None:
        amazonS3.delete(deletefile)
        sys.exit()
        
    if restorefile != None:
        amazonS3.restore(restorefile)
        sys.exit()


     
    
    

if __name__ == "__main__":
    main()
		
















#response = conn.create_bucket(BUCKET_NAME)
#print response.http_response.status

#buckets = conn.list_all_my_buckets().entries;
#print map(lambda x: x.name, conn.list_all_my_buckets().entries)
#print buckets;

'''
archive_file = open("/home/jayesh/workspace/snapshots/altvideo.2007-05-27-17_27.tar.gz")
archive_file_data = archive_file.read();

print conn.put(
        BUCKET_NAME,
        'backup.tar.gz',
        S3.S3Object(archive_file_data),
        { 'Content-Type': 'application/x-gzip' }).http_response.reason

archive_file_data = conn.get(BUCKET_NAME, 'backup.tar.gz').object.data
archive_file = open("/tmp/backup.tar.gz","w");

archive_file.write(archive_file_data);
archive_file.close();
'''

#print map(lambda x: x.key, conn.list_bucket(BUCKET_NAME).entries)


#print conn.get(BUCKET_NAME, KEY_NAME).object.data


'''
print '----- creating bucket -----'
print conn.create_bucket(BUCKET_NAME).http_response.reason

print '----- listing bucket -----'
print map(lambda x: x.key, conn.list_bucket(BUCKET_NAME).entries)

print '----- putting object (with content type) -----'
print conn.put(
        BUCKET_NAME,
        KEY_NAME,
        S3.S3Object('this is a test'),
        { 'Content-Type': 'text/plain' }).http_response.reason

print '----- listing bucket -----'
print map(lambda x: x.key, conn.list_bucket(BUCKET_NAME).entries)

print '----- getting object -----'
print conn.get(BUCKET_NAME, KEY_NAME).object.data

print '----- query string auth example -----'
print "\nTry this url out in your browser (it will only be valid for 60 seconds).\n"

generator = S3.QueryStringAuthGenerator(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, False)
generator.set_expires_in(60);
url = generator.get(BUCKET_NAME, KEY_NAME)
print url
print '\npress enter> ',
sys.stdin.readline()

print "\nNow try just the url without the query string arguments.  it should fail.\n"
print generator.make_bare_url(BUCKET_NAME, KEY_NAME)
print '\npress enter> ',
sys.stdin.readline()


print '----- putting object with metadata and public read acl -----'
print conn.put(
    BUCKET_NAME,
    KEY_NAME + '-public',
    S3.S3Object('this is a publicly readable test'),
    { 'x-amz-acl': 'public-read' , 'Content-Type': 'text/plain' }
).http_response.reason

print '----- anonymous read test ----'
print "\nYou should be able to try this in your browser\n"
public_key = KEY_NAME + '-public'
print generator.make_bare_url(BUCKET_NAME, public_key)
print "\npress enter> ",
sys.stdin.readline()

print "----- getting object's acl -----"
print conn.get_acl(BUCKET_NAME, KEY_NAME).object.data

print "----- vanity domain example -----"
print "\nThe bucket can also be specified as part of the domain.  Any vanity domain that is CNAME'd to s3.amazonaws.com is also valid."
print "Try this url out in your browser (it will only be valid for 60 seconds).\n"
generator.calling_format = S3.CallingFormat.SUBDOMAIN
url = generator.get(BUCKET_NAME, KEY_NAME)
print url
print "\npress enter> ",
sys.stdin.readline()

print '----- deleting objects -----'
print conn.delete(BUCKET_NAME, KEY_NAME).http_response.reason
print conn.delete(BUCKET_NAME, KEY_NAME + '-public').http_response.reason

print '----- listing bucket -----'
print map(lambda x: x.key, conn.list_bucket(BUCKET_NAME).entries)

print '----- listing all my buckets -----'
print map(lambda x: x.name, conn.list_all_my_buckets().entries)

print '----- deleting bucket ------'
print conn.delete_bucket(BUCKET_NAME).http_response.reason
'''
