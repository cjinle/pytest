#!/usr/bin/env python
# -*- coding: utf-8 -*-


def f(max):
    n, a, b = 0, 0, 1
    while n < max:
        #print b
        yield b
        a, b = b, a + b
        n = n + 1


for i in f(5):
    print i

