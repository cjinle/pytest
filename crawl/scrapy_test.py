#!/usr/bin/evn python
# -*- coding: utf-8 -*-

from scrapy import log

log.start('./scrapy_test.log')
log.msg('hello world c', log.CRITICAL)
log.msg('hello world error', log.ERROR)
log.msg('hello world debug', log.WARNING)
log.msg('hello world',)

print dir(log)