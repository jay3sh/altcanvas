#!/usr/bin/env python

import os

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
        
        
def main():
    archiver = Archiver('test.tar','test.snar',['/home/jayesh/workspace/sdlswf' '/home/jayesh/workspace/temp'])
    archiver.compress()

if __name__ == "__main__":
    main()
