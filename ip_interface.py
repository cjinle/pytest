#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json

url = 'http://api.tdbank.oa.com/query?queryid=3&businessid=b_hy_welink'
req = urllib2.urlopen(url)
str = req.read()

d1 = json.loads(str)

str2 = d1['returnStr']

d2 = json.loads(str2)

for i in d2:
    print "---------"
    for k, v in i.items():
        print k, ':', v