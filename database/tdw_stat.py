#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自动获取完整度最近数据到另一统计表
"""


import sys
import json
import datetime
import time
import ConfigParser
import MySQLdb
import MySQLdb.cursors
from common import Log

class TdwIntegrity:
    log_obj = None
    tdw_con = None
    tdw_cursor = None
    stat_con = None
    stat_cursor = None
    meta_con = None
    meta_cursor = None
    def __init__(self, **cfg):
        self.log_obj = Log(cfg['log_file'])
        self.meta_con = MySQLdb.connect(host=cfg['db_meta_host'], user=cfg['db_meta_user'], passwd=cfg['db_meta_pwd'], 
                                      db=cfg['db_meta_name'], charset='utf8', use_unicode=True, 
                                      cursorclass=MySQLdb.cursors.DictCursor)
        self.tdw_con = MySQLdb.connect(host=cfg['db_tdw_host'], user=cfg['db_tdw_user'], passwd=cfg['db_tdw_pwd'], 
                                      db=cfg['db_tdw_name'], charset='utf8', use_unicode=True, 
                                      cursorclass=MySQLdb.cursors.DictCursor)
        self.stat_con = MySQLdb.connect(host=cfg['db_stat_host'], user=cfg['db_stat_user'], passwd=cfg['db_stat_pwd'], 
                                      db=cfg['db_stat_name'], charset='utf8', use_unicode=True, 
                                      cursorclass=MySQLdb.cursors.DictCursor)
        self.meta_cursor = self.meta_con.cursor()
        self.tdw_cursor = self.tdw_con.cursor()
        self.stat_cursor = self.stat_con.cursor()
        
    def getLast7Dasy(self, d):
        ret = []
        for i in range(8):
            tmp = d - datetime.timedelta(days=i)
            ret.append(str(tmp))
        return ret
        
    def getReportServiceIDs(self):
        ret = []
        sql = "SELECT iSerID FROM md_service_list WHERE iDailyReport>0"
        self.meta_cursor.execute(sql)
        for i in self.meta_cursor.fetchall():
            ret.append(int(i['iSerID']))
        return ret
    
    def getTdwStore(self, serID, date):
        ret = 0
        tbName = "md_quainterity_res_%s_%s" % (serID, date.replace('-', '')[0:6])
        sql = "SELECT SUM(vToResult) as cnt FROM %s WHERE iMetaQuaID=5 AND vFieldInterval LIKE '%s%%'" % (tbName, date)
        try:
            self.tdw_cursor.execute(sql)
            fetchone = self.tdw_cursor.fetchone()
            if fetchone['cnt'] > 0:
                ret = fetchone['cnt']
        except Exception as e:
            self.log("getTdwStore: %s, params: [%s, %s]" % (e, serID, date), 'error')
        return ret
    
    def insertStatTdwStore(self, data):
        sql = "INSERT INTO md_stat_integrity_day (iSerID, iMetaQuaID, dDate, iStore) " \
              " VALUES ('%s', '5', '%s', '%s') " % (data['iSerID'], data['dDate'], data['iStore'])
        try:
            self.stat_cursor.execute(sql)
            self.stat_cursor.execute("commit")
        except Exception as e:
            self.log("%s, params: [%s]" % (e, str(data)), 'error')
    
    def updateStatTdwStore(self, store, iID):
        sql = "UPDATE md_stat_integrity_day SET iStore='%s' WHERE iID='%s' " % (store, iID)
        try:
            self.stat_cursor.execute(sql)
            self.stat_cursor.execute("commit")
        except Exception as e:
            self.log("updateStatTdwStore: %s, params: [store: %s, iID: %s]" % (e, store, iID), 'error')      
            
    def checkStatTdwStoreExist(self, data):
        ret = 0
        sql = "SELECT iID FROM md_stat_integrity_day WHERE iSerID='%s' AND iMetaQuaID=5 AND dDate='%s' LIMIT 1" % (data['iSerID'], data['dDate'])
        try:
            self.stat_cursor.execute(sql)
            fetchone = self.stat_cursor.fetchone()
            if fetchone['iID'] > 0:
                ret = fetchone['iID']
        except Exception as e:
            self.log("checkStatTdwStoreExist: %s, params: [%s]" % (e, str(data)), 'error')
        finally:
            return ret
        
    def checkTop10StoreTableExist(self, serID, date, tbName):
        ret = 0
        sql = "SELECT iID FROM md_stat_integrity_table WHERE iSerID='%s' AND iMetaQuaID=5 AND dDate='%s' AND vTbName='%s' LIMIT 1" % (serID, date, tbName)
        try:
            self.stat_cursor.execute(sql)
            fetchone = self.stat_cursor.fetchone()
            if fetchone['iID'] > 0:
                ret = fetchone['iID']
        except Exception as e:
            self.log("checkTop10StoreTableExist: %s, params: [%s]" % (e, str((serID, date, tbName))), 'error')
        finally:
            return ret     
        
    def tdwTop10StoreTables(self, serID, date):
        ret = []
        tbName = "md_quainterity_res_%s_%s" % (serID, date.replace('-', '')[0:6])
        sql = "SELECT vToDataField, SUM(vToResult) as cnt FROM %s WHERE iMetaQuaID=5 AND vFieldInterval LIKE '%s%%' GROUP BY vToDataField ORDER BY SUM(vToResult) DESC LIMIT 10" % (tbName, date)
        try:
            self.tdw_cursor.execute(sql)
            ret = self.tdw_cursor.fetchall()
        except Exception as e:
            self.log("tdwTop10StoreTables: %s, params: [%s, %s]" % (e, serID, date), 'error')
        if ret:
            for i in ret:
                iID = self.checkTop10StoreTableExist(serID, date, i['vToDataField'])
                if iID > 0:
                    sql = "UPDATE md_stat_integrity_table SET iStore='%s' WHERE iID='%s'" % (i['cnt'], iID)
                else:
                    sql = "INSERT INTO md_stat_integrity_table (iSerID, iMetaQuaID, dDate, vTbName, iStore) " \
                          " VALUES ('%s', 5, '%s', '%s', '%s') " % (serID, date, i['vToDataField'], i['cnt'])
                try:
                    self.stat_cursor.execute(sql)
                except Exception as e:
                    self.log("tdwTop10StoreTables: %s, params: [%s, %s, %s]" % (e, serID, date, str(i)), 'error')
                finally:
                    self.stat_cursor.execute("commit")
    
            
    def log(self, msg, level='info'):
        self.log_obj.log(msg, level)
    
        

if __name__ == "__main__":
    d = datetime.date.today()
    if len(sys.argv) > 1:
        year, month, day = sys.argv[1].split('-')
        d = datetime.date(int(year), int(month), int(day))
    cfg = ConfigParser.ConfigParser()
    cfg.read(sys.path[0] + '/tdw_stat.cfg')
    config = dict(cfg._sections['default'])
    
    ti = TdwIntegrity(**config)
    days = ti.getLast7Dasy(d)
    ids = ti.getReportServiceIDs()
    for i in days:
        for j in ids:
            print i, j
            store = ti.getTdwStore(j, i)
            data = {
                    'iSerID' : j,
                    'dDate' : i,
                    'iStore' : store
                    }
            iID = ti.checkStatTdwStoreExist(data)
            if iID > 0:
                ti.updateStatTdwStore(store, iID)
            else:
                ti.insertStatTdwStore(data)
          
#    yesterday = str(d - datetime.timedelta(days=1))
#    for i in ids:
#        print i
#        ti.tdwTop10StoreTables(i, yesterday)
    ti.log("%s DONE!" % str(d))
    print 'done!'
    

           
    
    
    
