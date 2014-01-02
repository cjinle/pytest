#!/usr/bin/env python
# coding: utf-8

"""
backup python script
author: Lok 2014/1/2
"""
import os
import subprocess
import ConfigParser
import logging
from time import time, strftime
from ftplib import FTP

class SaveFTP:
    """FTP上传类"""
    
    host = 'localhost'
    user = 'root'
    pwd = ''
    file = ''
    del_file = False
    remote_dir = '/stats/bak00/'
    ftp = None
    def __init__(self, **config):
        self.host = config['host']
        self.user = config['user']
        self.pwd = config['pwd']
        self.login()
    
    def login(self):
        try:
            self.ftp = FTP(self.host)
            self.ftp.login(self.user, self.pwd)
        except Exception as e:
            logging.error("SaveFTP::login() Exception: %s" % e)
    
    def send(self, file='', remote_dir=''):
        if not file: file = self.file
        if not remote_dir: remote_dir = self.remote_dir
        try:
            self.ftp.cwd(remote_dir)
            f = open(file,'rb')
            self.ftp.storbinary('STOR ' + file, f, 1024)
            self.ftp.close()
            if self.del_file: os.remove(file)
        except Exception as e:
            logging.error("SaveFTP::send() Exception: %s" % e)
        

class DumpMySQL:
    """把mysql dump成sql,然后再打包"""
    host = 'localhost'
    user = 'root'
    pwd = ''
    db_name = 'test'
    sql_file = ''
    tar_file = ''
    def __init__(self, **config):
        self.host = config['host']
        self.user = config['user']
        self.pwd = config['pwd']
        self.db_name = config['db_name']
        self.dump()
    
    def dump(self):
        self.sql_file = "%s_%s.sql" % (self.db_name, strftime("%Y%m%d%H%M%S"))
        cmd = "mysqldump -h%s -u%s -p%s %s > %s" % (self.host, self.user, self.pwd, self.db_name, self.sql_file)
        logging.info("dumpMySQL::dump() cmd: %s" % cmd);
        try:
            subprocess.call(cmd, shell=True)
        except Exception as e:
            logging.error("dumpMySQL::dump() Exception: %s" % e);
    
    def tar(self):
        self.tar_file = self.sql_file + '.tar.gz'
        cmd = "tar czf %s %s" % (self.tar_file, self.sql_file)
        try:
            subprocess.call(cmd, shell=True)
            os.remove(self.sql_file)
            return self.tar_file
        except Exception as e:
            logging.error("dumpMySQL::tar() Exception: %s" % e);
    


# get config file
config = ConfigParser.ConfigParser()
if os.path.dirname(__file__):
    dir = os.path.dirname(__file__)
else:
    dir = './'
config.read(dir + '/bak.cfg')

# log init
fmt = "%(asctime)s - %(levelname)s - %(message)s"
datefmt = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(filename = '%s/bak.log' % dir, level = logging.DEBUG, format=fmt, datefmt=datefmt)

# dump mysql sql file
db_config = config._sections['db']
dm = DumpMySQL(**db_config)
file = dm.tar()

# upload to ftp server
ftp_config = config._sections['ftp']
sf = SaveFTP(**ftp_config)
sf.send(file)
os.remove(file) # delete tar file
    
        
