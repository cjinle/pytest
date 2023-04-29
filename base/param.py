#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Cls:
    def func1(self, *args):
#        print args
        for i in args:
            print i
    
    def func2(self, **kwargs):
#        print kwargs
        for k, v in kwargs.items():
            print k,":", v
        

a = Cls()

a.func1(1, 2, 3)
a.func2(name="jinle", age=10)