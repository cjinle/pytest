#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

fmt = "%(asctime)s - %(levelname)s - %(message)s"
datefmt = '%Y-%m-%d %H:%M:%S'

logging.basicConfig(filename = 'log.log', level = logging.DEBUG, format=fmt, datefmt=datefmt)
logging.info("hello world")
#logger = logging.getLogger("log.log")
#logger.setLevel(logging.DEBUG)
#
#ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
#
#fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#ch.setFormatter(fmt)
#
#logger.addHandler(ch)
#
#logger.debug('this is test for log debug!')
#logger.info('this is test for log info!')