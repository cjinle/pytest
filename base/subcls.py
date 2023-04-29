#!/usr/bin/env python


class A(object):
    def foo(self):
        print "A.foo()"


class B(A):
    def foo(self):
        print "B.foo()"
        super(B, self).foo()


b = B()
b.foo()