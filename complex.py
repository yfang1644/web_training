#!/usr/bin/env python
# encoding: utf-8
# File Name: complex.py
# Author: Fang Yuan (yfang@nju.edu.cn)
# Created Time: Sat 28 Jan 2017 08:25:08 PM CST


class Complex():
    def __init__(self, real=0, imag=0):
        self.real = real
        self.imag = imag

    def __str__(self):
        return str(self.real) + '+' + str(self.imag)
    def __add__(self, other):
        return Complex(self.real + other.real, self.imag + other.imag)

c = Complex(1, 2)
b = Complex(2, -1.2)
print (b + c)
