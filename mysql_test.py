#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
import mysql.connector

class MySQLCursorDict(mysql.connector.cursor.MySQLCursor):
    def _row_to_python(self, rowdata, desc=None):
        row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
        if row:
            return dict(zip(self.column_names, row))
        return None

cnx = mysql.connector.connect(user='root', password='', 
                              host='localhost', database='test')
                             

# print dir(MySQLCursorDict)
cur = cnx.cursor(cursor_class=MySQLCursorDict)
sql = "select user,password from user"
cur.execute(sql)
rows = cur.fetchall()
pprint(rows)
cur.close()
cnx.close()