#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox()
url = 'http://www.baidu.com/'
driver.get(url)

driver.find_element_by_id('kw1').send_keys("hello world\n")
for i in range(100):
    driver.find_element_by_id('kw').clear()
    driver.find_element_by_id('kw').send_keys("%s\n" % i)
    time.sleep(0.5)

#driver.find_element_by_id('kw').clear()
#driver.find_element_by_id('kw').send_keys("test\n")




