# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 11:55:47 2019

@author: project
"""

import fileprocessing as fp
import wave
import numpy as np

song = wave.open('Media/44100hz.wav', 'rb')
print(song.getnframes())
param = song.getparams()

fp.writeToWaveMessage('0111111111111111'*698194, 'hello.wav', param)



print("{0:016b}".format(-1))
