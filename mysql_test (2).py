#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector

class Db():
    def __init__(self):
        config = {
          'host' : 'localhost',
          'user' : 'root',
          'password' : '',
          'database' : 'test'
          }
        self.conn = mysql.connector.connect(**config)
        self.cursor = self.conn.cursor()
    def query(self, sql):
        try:
            self.cursor.execute(sql)
        except Exception, e:
            print "Exception: ", e
    def getAll(self, sql):
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception, e:
            print "Exception: ", e
    def __del__(self):
        self.cursor.close()
        self.conn.close()

db = Db()
sql = "select * from a0"
aa = db.getAll(sql)
for i in aa:
    print i[0], i[1]

        
        
