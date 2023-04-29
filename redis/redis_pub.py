#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模拟redis pub （数据地图）
"""
import sys
import json
import redis
import MySQLdb
import MySQLdb.cursors

class RedisPub:
    redis_con = None
    db_con = None
    db_cursor = None
    def __init__(self, **cfg):
        self.redis_con = redis.StrictRedis(host=cfg['redis_host'], port=cfg['redis_port'], db=cfg['redis_db'])
        self.db_con = MySQLdb.connect(host=cfg['db_host'], user=cfg['db_user'], passwd=cfg['db_pwd'], 
                                      db=cfg['db_name'], charset='utf8', use_unicode=True, 
                                      cursorclass=MySQLdb.cursors.DictCursor)
        self.db_cursor = self.db_con.cursor()
        
    def get_event_log(self, date='201307', log_id=0):
        sql = "SELECT * FROM md_new_event_log_%s WHERE iID='%s'"  % (date, log_id)
        self.db_cursor.execute(sql)
        return self.db_cursor.fetchall()
        
    def pub_event_log(self, channel='test', message=''):
        self.redis_con.publish(channel, message)
    
    
if __name__ == "__main__":
    try:
        config = {
              'db_host' : '10.140.10.18',
              'db_name' : 'db_MetaDataMap',
              'db_user' : 'meta',
              'db_pwd' : 'meta@datamg',
              'redis_host' : '10.187.22.150',
              'redis_port' : 6379,
              'redis_db' : 5
              }
        rp = RedisPub(**config)
        msg = rp.get_event_log(sys.argv[1], sys.argv[2])[0]
        print msg
        if msg:
            message = {}
            message["iSerID"] = str(msg['iSerID'])
            message["iOperType"] = str(msg['iOperType'])
            message["iDistrictID"] = str(msg['iDistrictID'])
            message["iDataID"] = str(msg['iDistrictID'])
            message["iOperRes"] = str(msg['iOperRes'])
            message["vOperRes"] = str(msg['vOperRes'])
            message["vDesc"] = msg['vDesc'].encode('utf-8')
            message["vField1"] = str(msg['vField1'])
            message["vField2"] = str(msg['vField2'])
            message["vField3"] = str(msg['vField3'])
            message["vField4"] = str(msg['vField4'])
            message["vField5"] = str(msg['vField5'])
            message["vField6"] = str(msg['vField6'])
            message["vField7"] = str(msg['vField7'])
            message["vField8"] = str(msg['vField8'])
            print message
            rp.pub_event_log('ImetaEvent.'+message["iOperType"], json.dumps(message))
    except Exception as e:
        print e   


    
