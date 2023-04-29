#!/usr/bin/env python

###################
# backup.py
# --------
###################
#
# Author: Remigiusz Dymecki
# Contact: remigiusz@gmail.com
# License: GNU General Public License v2
# Platform: Unix/Linux/MacOSX only

from time import strftime
from ftplib import FTP

import os

class backup:

    def __init__(self,name, date_format):
        self.name = '%s-%s' % (name, strftime(date_format))
        self.files = []
        self.dirs =  []
        self.ftpes = []

    def addFiles(self,path):
        self.files.append(path)

    def copyToDir(self, path):
        self.dirs.append(path)

    def copyToFTP(self, host, user, passwd, path = '/'):
        ftp = {'host': host, 'user': user, 'passwd': passwd, 'path': path}
        self.ftpes.append(ftp)


    def backup(self):
        print '-------------------------------\\'
        print 'starting backup...'

        #pre
        #cmd = 'mkdir /tmp/%s' % (self.name)
        #os.system(cmd);
        cmd = 'touch /tmp/%s.tar' % (self.name)
        os.system(cmd);

        #compress files
        for file in self.files:
            cmd = 'tar -rf /tmp/%s.tar %s' % (self.name, file)
            os.system(cmd);

        #compress all
        cmd = 'bzip2 /tmp/%s.tar' % self.name
        os.system(cmd);

        #move
        for dir in self.dirs:
            cmd = 'cp /tmp/%s.tar.bz2 %s' % (self.name, dir)
            os.system(cmd);

        #ftpes
        for ftp in self.ftpes:
            session = FTP(ftp['host'])
            session.login(ftp['user'], ftp['passwd'])
            session.cwd(ftp['path'])
            f = open('/tmp/%s.tar.bz2' % self.name,'rb')
            session.storbinary('STOR ' + '%s.tar.bz2' % self.name, f, 1024)
            session.close()

        #clean
        cmd = 'rm /tmp/%s.tar.bz2' % self.name
        os.system(cmd);
        #cmd = 'rm -r /tmp/%s' % (self.name)
        #os.system(cmd);

        print '... finished'
        print '-------------------------------/'