# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 14:10:15 2019

@author: project
"""

import geneticAlgorithm as GA
import numpy as np

print("##################################################")
print("######    Tesitng GA operations with Ei = 1 ######")
print("##################################################")
      
sample = '1000000110000010'

print("Original amplitude:", int(sample, 2))
print("The original sample is: ", sample)

population, replacedBits = GA.generatePopulation(sample, '1')
    
print("")

print("Population after one is inserted:")

for i in population:
    print(i)
print("")

print("Replaced bits are:", replacedBits)

print("")
          
population = GA.generateNextGeneration(population, replacedBits, '1')

print("Second Generation (GA insertion)")
for i in population:
    print(i, "Amplitude:", np.abs(int(i, 2) - int(sample, 2)))

print("")
print("##################################################")
print("######    Tesitng determine fittest individual ###")
print("##################################################")
      
print(GA.determineFittest(sample, population))

print("##################################################")
print("######    Tesitng GA operations with Ei = 0 ######")
print("##################################################")
      
sample = '1000000110000010'

print("Original amplitude:", int(sample, 2))
print("The original sample is: ", sample)

population, replacedBits = GA.generatePopulation(sample, '0')
    
print("")

print("Population after one is inserted:")

for i in population:
    print(i)
print("")

print("Replaced bits are:", replacedBits)

print("")
          
population = GA.generateNextGeneration(population, replacedBits, '0')

print("Second Generation (GA insertion)")
for i in population:
    print(i, "Amplitude:", np.abs(int(i, 2) - int(sample, 2)))
    
print("")
 
print("##################################################")
print("######    Tesitng determine fittest individual ###")
print("##################################################")
      
print(GA.determineFittest(sample, population))
