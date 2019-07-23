# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 14:10:15 2019

@author: project
"""

import fileprocessing as fp
import geneticAlgorithm as GA
import wave

print("##################################################")
print("######      Tesitng generate population     ######")
print("##################################################")
      
song = wave.open('Media/opera.wav', 'rb')
samples = fp.extractWaveSamples(song)[0]

print("Original Sample: ", "{0:016b}".format(samples[0]))

population = GA.generatePopulation("{0:016b}".format(samples[0]), '1')

print("Population is:")

for i in population:
    print(i)
    
print("##################################################")
print("######    Tesitng crossOverOnes function    ######")
print("##################################################")
      
print("Original Sample:", "{0:016b}".format(samples[0]))      
print("Crossover start = -15, end = -1", "".join(GA.crossOverOnes(-15,-1, list("{0:016b}".format(samples[0])))))

print("Original Sample:", "{0:016b}".format(samples[0]))      
print("Crossover start = 1, end = 15", "".join(GA.crossOverOnes(-4,-3, list("{0:016b}".format(samples[0])))))

print("##################################################")
print("######    Tesitng generate next generation  ######")
print("##################################################")
      
sample = '1000000110000010'
      
print("The original sample is: ", sample)

population = GA.generatePopulation(sample, '1')

print("Population after one is inserted:")

for i in population:
    print(i)
 
print(population)       
population = GA.generateNextGeneration(population)

print("Next generation:")

for i in population:
    print(i)

'''    
population = GA.generatePopulation(sample, '0')

print("Population after zero is inserted:")

for i in population:
    print(i)
'''