#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlopen
import datetime
import time

from common import Log

if __name__ == "__main__":
    logfile = '/home/sap/v_jinlchen/integrity.log'
    log = Log(logfile)
    host = 'http://imeta.ied.com'
    day = datetime.date.today() - datetime.timedelta(days=2)
    service_list = [1,3,4,49]
    url = host + '/index.php/nologin/drIntegrity/%s/' + str(day) + '/1'
    if service_list:
        for i in service_list:
            ret = urlopen(url % i).read()
            print ret
            time.sleep(1)
            if ret == "1":
                log_type = 'info'
            else:
                log_type = 'error'
            log.log(ret + " - " + url % i, log_type)