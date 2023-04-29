#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import Common, Test, Log

a = Common()
b = Test()
#c = Log()
d = Log('./log.log')


b.hello()
#c.log('123123123')
d.log('1231ssssssss23123', 'error')
