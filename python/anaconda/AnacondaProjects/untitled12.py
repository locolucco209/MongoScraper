#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 15:49:27 2017

@author: lukemassetti
"""

bol_one = False or not True and True 
bol_two = False and not True or True
bol_three = True and not (False or False)
bol_four = not not True or False and not True
bol_five = False or not (True and True)

print bol_one, bol_two, bol_three, bol_four, bol_five,