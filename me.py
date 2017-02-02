#!/usr/bin/env python
# encoding: utf-8
# File Name: me.py
# Author: Fang Yuan (yfang@nju.edu.cn)
# Created Time: Sat 28 Jan 2017 01:36:47 PM CST


class Animal:
    __name = ""
    __height = 0
    __weight = 0
    __sound = 0

    def __init__(self, name, height, weight, sound):
        self.__name = name
        self.__height = height
        self.__weight = weight
        self.__sound = sound

    def set_name(self, name):
        __name = name

    def get_name(self):
        return self.__name

    def set_height(self, height):
        self.__height = height

    def get_type(self):
        print()

    def toString(self):
        return "{} is {} cm tall and {} kg and say {}".format(self.__name,
                                                              self.__height,
                                                              self.__weight,
                                                              self.__sound)

xxx = 6

def test():
    xxx = 5


cat = Animal("whisker", 22, 10, 'meow')
print cat.toString()

print ("first %d" %(xxx))
test()
print ("second %d" %(xxx))

