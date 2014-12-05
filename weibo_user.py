#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import Connection

c = Connection()
collection = c.sina.weibo_user

f = open('index.html', 'w')
f.write('<html><head><meta charset="utf-8"></head><body>')

for user in collection.find():
    for fan in user['fans']:
        tmp = "<a href='http://weibo.com/%s' taraget='_blank'>%s</a>\n<br>" % (str(fan['uid']), str(fan['nickname'].encode('UTF-8')))
        f.write(tmp)

    for follow in user['follows']:
        tmp = "<a href='http://weibo.com/%s' taraget='_blank'>%s</a>\n<br>" % (str(follow['uid']), str(follow['nickname'].encode('UTF-8')))
        f.write(tmp)
    print user

f.write('</body></html>')
f.close()