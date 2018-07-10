#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 14:41:05 2017

@author: lukemassetti
"""

from datetime import datetime

now = datetime.now()

print now.hour
print now.minute
print now.second

print '%s:%s:%s' % (now.hour, now.minute, now.second)

from datetime import datetime
now = datetime.now()

print '%s/%s/%s' %(now.month, now.day, now.year)
print '%s:%s:%s' % (now.hour, now.minute, now.second)

print '%s/%s/%s %s:%s:%s' %(now.month, now.day, now.year, now.hour, now.minute, now.second)
