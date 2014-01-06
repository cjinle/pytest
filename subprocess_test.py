#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess


cmd = "ls /xxx"
out = ''
err = ''
fp = open('a.txt', 'wb')

subprocess.call(cmd, stdout=fp, stderr=subprocess.STDOUT, shell=True)
