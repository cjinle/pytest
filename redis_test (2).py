#!/usr/bin/env python
# -*- coding: utf-8 -*-


import redis

r = redis.StrictRedis(host='10.12.16.45', port=6379, db=10)


print "---\n"
for i in range(100):
    r.publish('test', "hello world 123")