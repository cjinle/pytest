#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Pizza(object):
    def __init__(self):
        self.toppings = []
    def __call__(self, topping):
        self.toppings.append(topping())
    def __repr__(self):
        return str(self.toppings)
    
pizza = Pizza()

@pizza
def func1():
    return "func1"

@pizza
def func2():
    return "func2"

print pizza