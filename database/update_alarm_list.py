#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
把旧规则收敛记录更新为新规则  2013-09-11
"""


import sys
import datetime
import time
import ConfigParser
import MySQLdb
import MySQLdb.cursors
from common import Log

class UpdateAlarmList:
    log_obj = None
    meta_con = None
    meta_cursor = None
    def __init__(self, **cfg):
        self.log_obj = Log(cfg['log_file'])
        self.meta_con = MySQLdb.connect(host=cfg['db_meta_host'], user=cfg['db_meta_user'], passwd=cfg['db_meta_pwd'], 
                                      db=cfg['db_meta_name'], charset='utf8', use_unicode=True, 
                                      cursorclass=MySQLdb.cursors.DictCursor)
        self.meta_cursor = self.meta_con.cursor()
        
    def getConvergingRecords(self, tbName):
        sql = "SELECT iAlarmListID,vFieldInterval,iRelateAlarmListID FROM %s WHERE iDealReport=0" % tbName
        self.meta_cursor.execute(sql)
        return self.meta_cursor.fetchall();
    
    def getAlarmListInfo(self, alarmListID, tbName):
        try:
            sql = "SELECT vFieldInterval,vFieldInterDetail FROM %s WHERE iAlarmListID=%s LIMIT 1" % (tbName, alarmListID)
#            self.log("getAlarmListInfo SQL: <%s>" % sql, 'info')
            self.meta_cursor.execute(sql)
            return self.meta_cursor.fetchone();
        except Exception as e:
            self.log("getAlarmListInfo: %s, params: <alarmListID: %s, tbName: %s>" % (e, alarmListID, tbName), 'error')
    
    def updateIntervalDetail(self, detailStr, alarmListID, tbName):
        try:
            sql = "UPDATE %s SET vFieldInterDetail='%s' WHERE iAlarmListID='%s' LIMIT 1" % (tbName, detailStr, alarmListID)
            self.meta_cursor.execute(sql)
            self.meta_cursor.execute("commit")
        except Exception as e:
            self.log("updateIntervalDetail: %s, params: <detailStr: %s, alarmListID: %s, tbName: %s>" % (e, detailStr, alarmListID, tbName), 'error')
            
    def getIntervalDetailStr(self, detailStr, interval1, interval2):
        diff = self.getHourDiff(interval1, interval2)
        length = len(detailStr)
        li = list(detailStr)
        if length >= diff:
            li.append('1')
#            li[diff] = '1'
        else:
            for i in range(diff+1):
                try:
                    if li[i]: pass
                except IndexError:
                    if i == diff:
                        li.append('1')
                    else:
                        li.append('0')
        return ''.join(li)

    def getHourDiff(self, interval1, interval2):
        ts1 = time.mktime(time.strptime(interval1[0:13], "%Y-%m-%d_%H"))
        ts2 = time.mktime(time.strptime(interval2[0:13], "%Y-%m-%d_%H"))
        return int((ts2 - ts1) / 3600)

    def log(self, msg, level='info'):
        self.log_obj.log(msg, level)
        

if __name__ == "__main__":
    cfg = ConfigParser.ConfigParser()
    cfg.read(sys.path[0] + '/tdw_stat.cfg')
    config = dict(cfg._sections['default'])
    ual = UpdateAlarmList(**config)
    #tbName = 'md_alarm_list'
    tbName = 'md_alarm_list_DT'
    detailStr = ''
    cr = ual.getConvergingRecords(tbName)
    for i in cr:
        tmpAlarmInfo = ual.getAlarmListInfo(i['iRelateAlarmListID'], tbName)
        if tmpAlarmInfo:
            logMsg = i['iRelateAlarmListID'], tmpAlarmInfo['vFieldInterval'], i['vFieldInterval']
            print logMsg
#            ual.log("update info: <%s>" % str(logMsg))
            detailStr = ual.getIntervalDetailStr(tmpAlarmInfo['vFieldInterDetail'], tmpAlarmInfo['vFieldInterval'], i['vFieldInterval'])
            ual.updateIntervalDetail(detailStr, i['iRelateAlarmListID'], tbName)
#        else:
#            print i['iRelateAlarmListID'], i['vFieldInterval']
    
