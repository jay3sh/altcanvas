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
        cmd += "--file %s "%self.archive_filename
        cmd += "--listed-incremental %s "%self.snapshot_filename
        for dir in self.backup_list:
            cmd += "%s "%dir
        print "Executing: %s"%cmd
        os.system(cmd);
        
    def extract(self):
        os.system('');
        
def usage():
    print "Archiver.py [options] <backup_list>"
    print "Options:"
    print "        -h --help    this help"
    print "        -n --name    Name to identify the backup project"
    print "        -t --type    FULL or INCR"
    print ""
    print "        backup_list  Comma separated list of files/dirs to backup" 
        
def main():
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hn:t:", 
                        ["help","name=","type="])
    except getopt.GetoptError:
        usage()
        sys.exit(0)

    type = None

    backup_list_str = sys.argv[-1]

    if not backup_list_str or not opts:
        usage()
        sys.exit(0)

    for o,a in opts: 
        if o in ("-h","--help"):
            usage()
            sys.exit()
        if o in ("-n","--name"):
            bname = a
        if o in ("-t","--type"):
            type = a

    tar_name = bname+".tar"
    snar_name = bname+".snar"

    if not type:
        type = "FULL"

    if type == "FULL":
        # if snar file exists
        if os.access(snar_name,os.F_OK):
            # if it is deletable
            if os.access(snar_name,os.W_OK):
                os.remove(snar_name)
            else:
                print "Can't delete existing SNAR file"
                sys.exit(1)


    backup_list = backup_list_str.strip().split(',')

    archiver = Archiver(tar_name,snar_name,backup_list)
    archiver.compress()

if __name__ == "__main__":
    main()
