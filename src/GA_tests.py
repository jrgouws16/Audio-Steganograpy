# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 13:59:43 2019

@author: project
"""

import wave

song = wave.open('Media/song.wav', mode='rb')

print(song.getframerate())

print(4814784/22050/60)