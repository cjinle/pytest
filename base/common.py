#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

"""
common class
"""

class Common:
    def __init__(self):
        print "common class load"
        

class Test:
    def __init__(self):
        print "test class load"
    def hello(self):
        print "hello world"
        
class Log:
    fmt = '%(asctime)s - %(levelname)s - %(message)s'
    def __init__(self, logfile = './common.log'):
        logging.basicConfig(filename=logfile, level=logging.DEBUG, format=self.fmt)
        
    def log(self, log_msg, level='debug'):
        if level == 'debug':
            logging.debug(log_msg)
        elif level == 'warning':
            logging.warning(log_msg)
        elif level == 'error':
            logging.error(log_msg)
        elif level == 'critical':
            logging.error(log_msg)
        else:
            logging.info(log_msg)
            
