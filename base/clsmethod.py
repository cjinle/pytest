#!/usr/bin/env python
# -*- coding: utf-8 -*-

class A(object):
    def foo(self,x):
        print "executing foo(%s,%s)"%(self,x)

    @classmethod
    def class_foo(cls,x):
        print "executing class_foo(%s,%s)"%(cls,x)

    @staticmethod
    def static_foo(x):
        print "executing static_foo(%s)"%x    

if __name__ == "__main__":
    a = A()

    a.foo(1)
    a.class_foo(1)
    A.class_foo(1)
    a.static_foo(1)
    A.static_foo(1)
    print a.static_foo
    print A.static_foo


