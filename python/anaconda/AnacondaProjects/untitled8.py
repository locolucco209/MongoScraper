#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 20:38:27 2017

@author: lukemassetti
"""

bool_a = 170 < 300
bool_b = 10 == (2*5)
bool_c = 21 <= 21
bool_d = -25 >= -21
bool_e = 100 != (99+1)
print bool_a
print bool_b
print bool_c, bool_d, bool_e

# The dope program

print "Welcome to wheel of your future!"

answer = raw_input("Enter a,b,c, or d, and see your luck")

if answer == 'a':
    print "You will meet a beautiful stranger!"

if answer == 'b':
    print "You will meet a fateful encouter, beware..."

if answer == 'c':
    print "You will get a reward from your mom!"
    
if answer == 'd':
    print "Today your life will completely change!"
    
else:
    print "Take a hike hippie!"


    
    
    