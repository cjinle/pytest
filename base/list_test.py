#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

l = range(20)
l = [str(i).ljust(3) for i in l]
length = len(l)

for i in range(5, 20):
    p = int(math.ceil(float(length)/i))
    for j in range(p):
        print "".join(l[j*i:j*i+i])
