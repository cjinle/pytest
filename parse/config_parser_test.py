#!/usr/bin/evn python
# -*- coding: utf-8 -*-

import ConfigParser

config = ConfigParser.ConfigParser()
config.read('a.ini')

#print type(config.get('meta', 'db_meta_pwd'))
print dict(config._sections['meta'])