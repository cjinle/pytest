#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import Connection

c = Connection()
collection = c.sina.weibo_user
tb_follow = c.sina.weibo_follow

for user in collection.find():
    for fan in user['fans']:
        d = {"_id":fan['uid'],"uid":fan['uid'],"nickname":fan['nickname'].encode('UTF-8')}
        tb_follow.insert(d)

    for follow in user['follows']:
        d = {"_id":follow['uid'],"uid":follow['uid'],"nickname":follow['nickname'].encode('UTF-8')}
        tb_follow.insert(d)

print "done"
