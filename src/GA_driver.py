# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 14:10:15 2019

@author: project
"""

import fileprocessing as fp
import geneticAlgorithm as GA
import wave

song = wave.open('Media/song.wav', 'rb')

samples = fp.extractWaveSamples(song)

print(samples)
