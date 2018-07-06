#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 23:31:00 2018

@author: Matt
"""
import re
import sys

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]

temp_hold = list(sys.argv[1:])
temp_hold.sort(key=natural_keys)
file = open('Channels_Sorted.txt','w')
for item in temp_hold:
    file.write(item + '\n')
file.close()