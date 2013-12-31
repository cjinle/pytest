#!/usr/bin/env python
# -*- coding: utf-8 -*-


import string
import time
import sys


open("f:/workspace/pytest/a.txt", "w").write("%s" % str(time.strftime("%Y-%m-%d %H:%M:%S")))



values = { 'var':'foo' }

t = string.Template("""
Variable            :    $var
Escape              :    $$
Variable in text    :    ${var}iable
""")

print 'TEMPLATE:', t.substitute(values)

s = """
Variable            :    %(var)s
Escape              :    %%
Variable in text    :    %(var)siable
"""

print 'INTERPPOLATION:', s % values
