#!/usr/bin/env python

import ConfigParser

config = ConfigParser.ConfigParser()
config.read('en.xsh')
# print config._sections['defaults']
for k, v in config._sections['defaults'].items():
    print "key: %s, value: %s" % (k, v)


