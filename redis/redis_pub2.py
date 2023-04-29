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
        message = {}
        message["table"] = 'db_MetaDataMap.md_new_event_log_201308'
        
        print message
        rp.pub_event_log('ImetaEvent.0', json.dumps(message))
    except Exception as e:
        print e   


    
