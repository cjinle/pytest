#!/usr/bin/env python

import redis


# r = redis.StrictRedis(host='localhost', port=6379, db=0)
r = redis.Redis(host='localhost', port=6379, db=0)

print r.keys('*')

# for i in range(100):
#     r.set('foo%s' % i, 'bar%s' % i)
# print r.keys('*')

