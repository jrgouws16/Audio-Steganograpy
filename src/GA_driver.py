# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 14:10:15 2019

@author: project
"""

import geneticAlgorithm as GA
import numpy as np
import random

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


print("##################################################")
print("#    Tesitng the insertion algorithm as in paper #")
print("##################################################")
samples = ['1001010001001100','0101010111100111','0000100011110001'] * 10

print("Before insertion")
for i in samples:
    print(i)
    
message = '1010'
key = '1001001110100000'*2
stego, samplesUsed, bitsInserted = GA.insertMessage(samples, key, message, 'txt')
print(stego)
print("Message is:", message)
print("key is:", key)
print("")

print("After insertion")
for i in stego:
    print(i)

print("##################################################")
print("#   Tesitng the extraction algorithm as in paper #")
print("##################################################")
print(GA.extractMessage(stego, key))


print("##################################################")
print("#  Extensive testing of insertion and extraction #")
print("##################################################")
          
# Generate the samples, key, and message      
items = ['1','0']

for numberTests in range(0, 1000):
    samples = []
    message = ''
    key = "".join(random.choices(items, k = 26))
    
    for messageLength in range(0,100):
        samples.append("".join(random.choices(items, k = 16)))
        message += random.choice(items)
        key += random.choice(items)
        
    for i in range(0, 26):
        samples.append("".join(random.choices(items, k = 16)))
        
    stego, samplesUsed, bitsInserted = GA.insertMessage(samples, key, message, "txt")
    extractedMsg, fileType = GA.extractMessage(stego, key)
       

    
    if (message != extractedMsg):
        print("Error")
        break
    
    elif (numberTests == 999):
        print("Extensive testing: Passed all the tests")
  

