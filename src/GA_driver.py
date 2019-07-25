# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 14:10:15 2019

@author: project
"""

import geneticAlgorithm as GA
'''
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
    
'''

print("##################################################")
print("######    Tesitng generate next generation  ######")
print("##################################################")
      
sample = '1000000110000010'
      
print("The original sample is: ", sample)

population, replacedBits = GA.generatePopulation(sample, '1')

print("Replaced bits are:", replacedBits)
print("Population after one is inserted:")

population.reverse()
replacedBits.reverse()

for i in population:
    print(i)
      
population = GA.generateNextGeneration(population, replacedBits, 1)

print("Next generation:")
population.reverse()

for i in population:
    print(i)

'''    
population = GA.generatePopulation(sample, '0')

print("Population after zero is inserted:")

for i in population:
    print(i)
'''