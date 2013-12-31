# --*-- utf-8 --*--

import MySQLdb

con = MySQLdb.connect(host='localhost', user='root', passwd="")
cur = con.cursor()
sql = 'set names utf8'
cur.execute(sql)
sql = 'use test'
cur.execute(sql)
sql = 'select staff_id, staff_name, cn_name from wl_staff limit 100'
item = ("title", "word1,word2", "description", "content")
sql = "INSERT INTO posts (title, keyword, description, content) VALUES ('%s', '%s', '%s', '%s') " % item
print sql
cur.execute(sql)
data = cur.fetchall()

if data:
    for i in data:
        print i[1]

#print msg
