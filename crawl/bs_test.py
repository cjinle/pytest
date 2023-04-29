#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
beautiful soup test
"""

from bs4 import BeautifulSoup

soup = BeautifulSoup(open('test.html'))

table = soup.find("table", id="check_in_tbl")
soup2 = BeautifulSoup(str(table))
r = soup2.find_all("tr")
print len(r)
