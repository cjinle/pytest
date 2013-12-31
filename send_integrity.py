#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import sys
from urllib import urlopen
import logging
import datetime
import time

class Log:
    fmt = '%(asctime)s - %(levelname)s - %(message)s'
    logfile = '/home/sap/v_jinlchen/integrity.log'
    def __init__(self):
        logging.basicConfig(filename=self.logfile, level=logging.DEBUG, format=self.fmt)
        
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
            


if __name__ == "__main__":
    log = Log()
    host = 'http://imeta.ied.com'
    get_service_list_url = host + '/index.php/nologin/getReportServices'
    ret = urlopen(get_service_list_url).read()
    print ret
    log.log("report services: %s" % ret)
    service_list = []
    if ret:
        for i in ret.split(';'):
            tmp = i.split('|')
            if tmp:
                service_list.append((tmp[0], tmp[1]))
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    #service_list = [53,57,55,58,56,44,54]
    url = host + '/index.php/nologin/sendTdwIntegrity/%s/' + str(yesterday) + '/100/%s'
    if service_list:
        for i in service_list:
            ret = urlopen(url % (i[0], i[1])).read()
            print ret
            time.sleep(1)
            if ret == "1":
                log_type = 'info'
            else:
                log_type = 'error'
            log.log(ret + " - " + url % (i[0], i[1]), log_type)
                


