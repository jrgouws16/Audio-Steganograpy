#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 14:06:00 2019

@author: johan
"""

string = "Cool stuff"

file_handler = open("Media/text.txt", 'r')
string = file_handler.read()
file_handler.close()

print(string)