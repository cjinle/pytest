#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

today = datetime.date.today()
today = datetime.date(2014, 12, 6)
print today

d1 = today + datetime.timedelta(days=1)
d2 = today + datetime.timedelta(days=2)
d3 = today + datetime.timedelta(days=3)

print d1, d2, d3