#!/usr/bin/env python

import sys
import os
import getopt

class Archiver:
    archive_filename = None
    snapshot_filename = None
    backup_list = None
    def __init__(self,archive_name,snapshot_filename,backup_list):
        self.archive_filename = archive_name
        self.snapshot_filename = snapshot_filename
        self.backup_list = backup_list
        
    def compress(self):
        cmd = "tar "
        cmd += "--create "
        cmd += "--file=%s "%self.archive_filename
        cmd += "--listed-incremental=%s "%self.snapshot_filename
        for dir in self.backup_list:
            cmd += "%s "%dir
        #print "Executing: %s"%cmd
        os.system(cmd);
        
    def extract(self):
        os.system('');
        
def usage():
    print "Archiver.py [options] <backup_list>"
    print "Options:"
    print "        -h --help    this help"
    print "        -n --name    Name to identify the backup project"
    print ""
    print "        backup_list  Comma separated list of files/dirs to backup" 
        
def main():
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hn:", 
                        ["help","name="])
    except getopt.GetoptError:
        usage()
        sys.exit(0)

    backup_list = sys.argv[-1]
    if not opts:
        usage()
        sys.exit(0)

    for o,a in opts: 
        if o in ("-h","--help"):
            usage()
            sys.exit()
        if o in ("-n","--name"):
            bname = a

    tar_name = bname+".tar"
    snar_name = bname+".snar"

    '''
    archiver = Archiver(tar_name,snar_name,
                ['/home/jayesh/workspace/sdlswf',
                 '/home/jayesh/workspace/temp'])
    archiver.compress()
    '''

if __name__ == "__main__":
    main()
