#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import requests

d = {'User-Agent': 'Mozilla/5.0'}
url = "http://blog.csdn.net/ranking.html"
resp = requests.get(url, headers = d)
bs = BeautifulSoup(resp.content)
# print bs

for i in bs.findAll('div', {'class':'ranking ranking_blog'}):
    # print i
    for x in i.findAll('span', {'class': 'title'}):
        for y in x.findAll('a'):
            print y.text
        # text = x.find('a', {'class': 'title'})
        # print text
        # print text.find