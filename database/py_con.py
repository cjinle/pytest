#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector

config = {
          'host' : 'localhost',
          'user' : 'root',
          'password' : '',
          'database' : 'metadata'
          }

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

sql = "SELECT iTableID, vTableName, vTableDesc FROM tbDataTableList"
cursor.execute(sql)

result = cursor.fetchall()

for i in result:
#    print i
    print "ID: %d, EN_NAME: %s, CN_NAME: %s" % i

cursor.close()
cnx.close()