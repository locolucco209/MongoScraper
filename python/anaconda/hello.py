#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 15:44:28 2017

@author: lukemassetti
"""

# This program says hello and asks for my name

print ('Hello World!')

# ask for their name
print ('What is your name?') 
myName = input()
print ('It is good to meet you, ' + myName)
print ('the length of your name is:')
print (len(myName))

# ask for their age
print ('What is your age?') 
myAge = input()
print ('You will be ' + str(int(myAge) +1) + ' in a year.')
