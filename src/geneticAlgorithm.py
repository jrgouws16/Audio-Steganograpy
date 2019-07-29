# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 14:10:15 2019

@author: project
"""
import numpy as np
import SignalsAndSlots as SS

signalEmbedding = SS.SigSlot()
signalExtractingMessage = SS.SigSlot()

# Function that takes a 16-bit audio sample and generates 5 chromosomes
# of the sample, by inserting the bit in LSB positions 4 - 8
# The function also returns the data bits that were replaced, as it will be 
# used in later GA operations
def generatePopulation(sample, bit):
    
    population = []
    replacedBits = []
    
    for i in range(8, 13):
        addSample = list(sample)
        replacedBits.append(addSample[i])
        addSample[i] = bit
        population.append("".join(addSample))
        
    population.reverse()
    replacedBits.reverse()
        
    return population, replacedBits

# Function that takes a current population and generates a better population
def generateNextGeneration(population, replacedBits, Ei):
    
    # Convert population into a list of lists, in order to do bit operations
    for i in range(0, len(population)):
        population[i] = list(population[i])
        
    # i is the embedding position, corresponding with the first individual 
    # in the population. This is equal to paper value * -1 -1
    i = -4
        
    for j in range(0, len(population)):
        # embed the fitness value into the least significant 3 bits of sample
        embedFitness = list("{0:03b}".format(j))
        
        for m in range(13,16):
            population[j][m] = embedFitness[m - 13]
        
        # If message bit (Ei) is zero
        if (Ei == '0'):
            
            # If data bit at i is zero, do nothing
            if(replacedBits[j] == '0'):
                pass
                
            else:
                # If position bit of i is at -4, put 0 at i
                if (i == -4):
                    population[j][i] = '0'
                    # If data at i - 1 is 0, then perform mutation operation
                    # at position i - 1
                    if (population[j][i - 1] == '0'):
                        population[j][i - 1] == '1'
                                        
                # If position of i is at -8, put 0 in position i and perform
                # Crossover from i-1 to 3 with 1...11111 string
                if (i == -8):
                    population[j][i] = '0'
                    for o in range(i + 1, -3):
                        population[j][o] = '1'
                    
                # Put 0 at position i and perform crossover from i-1 to 3 
                # with 1...11111 string    
                else:
                    population[j][i] = '0'
                    for o in range(i + 1, -3):
                        population[j][o] = '1'                    
                    # if data bit at i + 1 is 0, then perform mutation at 
                    # position i + 1 and crossover operation at position from 
                    # i-1 to 3 with 000.00000 string
                    if (population[j][i - 1] == '0'):
                        population[j][i - 1] = '1'
                        for o in range(i + 1, -3):
                            population[j][o] = '0'
                        
        # If the message bit (Ei) is one    
        else:
            # If data bit at i is one, do nothing
            if(replacedBits[j] == '1'):
                pass
                           
            else:
                # If position bit of i is at -4, put 1 at i
                if (i == -4):
                    population[j][i] = '1'

                    # If data at i - 1 is 1, then perform mutation operation
                    # at position i - 1
                    if (population[j][i - 1] == '1'):
                        population[j][i - 1] == '0'
                        
                                       
                # If position of i is at -8, put 1 in position i and perform
                # Crossover from i-1 to 3 with 0...0000 string
                if (i == -8):
                    population[j][i] = '1'
                    for o in range(i + 1, -3):
                        population[j][o] = '0'                 
                # Put 1 at position i and perform crossover from i-1 to 3 
                # with 0...000000 string    
                else:
                    population[j][i] = '1'
                    
                    for o in range(i + 1, -3):
                        population[j][o] = '0'
                    # if data bit at i + 1 is 1, then perform mutation at 
                    # position i + 1 and crossover operation at position from 
                    # i-1 to 3 with 1111.1 string
                    if (population[j][i - 1] == '1'):
                        population[j][i - 1] = '0'
                        for o in range(i + 1, -3):
                            population[j][o] = '1'
        i = i - 1
            
    
    for l in range(0, len(population)):
        population[l] = "".join(population[l])
    
    return population

# Function to determine and return the best chromosome from a population of five
def determineFittest(originalSample, population):
    ampDifference = []
    returnIndex = 0

    # Determine the amplitude differences for each individual 
    for i in range(0, 5):
        ampDifference.append(np.abs(int(population[i], 2) - int(originalSample,2)))    
        
    # Get the smallest amplitude difference    
    smallest = min(ampDifference)
    
    # Get all the indexes where the smallest value occurs
    indexes = [i for i,x in enumerate(ampDifference) if x == smallest]
       
    # Preferred indexes is of fitness value between 0 and 4 exclusive
    # If this is not possible, choose the one with the smallest fitness value
    if 1 in indexes:
        returnIndex = 1
        
    elif 2 in indexes:
        returnIndex = 2
    
    elif 3 in indexes:
        returnIndex = 3
        
    elif 0 in indexes:
        returnIndex = 0
        
    elif 4 in indexes:
        returnIndex = 4
        
    return returnIndex

def insertMessage(samples, key, message):
   
    skipIndex = 0
    sampleIndex = 0
    
    messageLength = len(message)
    messageLength = '{0:024b}'.format(messageLength)
    
    message = messageLength + message
    
    for i in range(0, len(message)):
        signalEmbedding.trigger.emit(float(i + 1) * 100 / len(message))
        
        if(skipIndex == 1):
            skipIndex = 0
            continue

        # Get Pi, which will be the index of the sample for determining Ei
        pi = int(key[sampleIndex % len(key): ((sampleIndex % len(key)) + 3) % len(key) + 1],2)
            
        if (pi < 8):
            pi += 8
        
        Ei = '0'
        # If message bit coincides with sample[Pi], then Ei is 1 else Ei = 0
        if (samples[sampleIndex][-1*pi - 1] == message[i]):
            Ei = '1'
            
        else:
            Ei = '0'
                    
        # Create the five chromosomes by inserting Ei at five positions
        population, replacedBits = generatePopulation(samples[sampleIndex], Ei)
        
        # Generate the next generation by performing GA operations
        population = generateNextGeneration(population, replacedBits, Ei)
        
        # Replace sample with the fittest cromosome
        samples[sampleIndex] = population[determineFittest(samples[sampleIndex], population)]
        
        # If fitness value between 0 and 4 exclusive, insert another bit at i = 2
        if(determineFittest(samples[sampleIndex], population) > 0 and 
           determineFittest(samples[sampleIndex], population) < 4):
            
            
            # Calculate pi for m(i+1)
            i = i + 1
            
            # If message is already inserted
            if(i >= len(message)):
                break
            
            skipIndex = 1
            
            # Determine Ei            
            if (samples[sampleIndex][-1*pi - 1] == message[i]):
                Ei = '1'
                
            else:
                Ei = '0'

            # Insert the second bit at the third LSB layer
            samples[sampleIndex] = list(samples[sampleIndex])
            samples[sampleIndex][-3] = Ei
            samples[sampleIndex] = "".join(samples[sampleIndex])
            
        
        sampleIndex = sampleIndex + 1
        
        
    return samples
       
def extractMessage(samples, key):
    message = ''
    sampleIndex = 0
    
    # This is the amount of bits that will determine the message length
    messageLength = 24
    
    # While the full message has not been extracted
    while (len(message) < messageLength):
        
        # Get the fitness value of the stego sample
        F = int(samples[sampleIndex][13:16], 2)

        # If F not zero or four, then F = decimal of first two LSBs of sample
        if (F != 0 and F != 4):
            F = int(samples[sampleIndex][14:16], 2)

        # Calculate the decimal value of Bi
        pi = int(key[sampleIndex % len(key): ((sampleIndex % len(key)) + 3) % len(key) + 1], 2) 
        
        # Make it a value between 8 and 15 inclusive
        if (pi < 8):
                pi += 8
        
        # If the bit at S[F] is one, extract the bit at pi
        if (samples[sampleIndex][-1*F - 4] == '1'):
            message += samples[sampleIndex][-1*pi - 1]
            
        # Else extract the opposite of the bit at pi    
        else:
            if (samples[sampleIndex][-1*pi - 1] == '1'):
                message += '0'
                
            else:
                message += '1'

        # If the message size is determined, add it to the total message length
        if (len(message) == 24):
            messageLength = int(message, 2) + 24

        # Extract the second sample for the case where F is 1/2/3
        if (F > 0 and F < 4):
            if (len(message) == messageLength):
                break
            
            if (samples[sampleIndex][-3] == '1'):
                message += samples[sampleIndex][-1*pi - 1]
                
            else:
                if (samples[sampleIndex][-1*pi - 1] == '1'):
                    message += '0'
                    
                else:
                    message += '1'
                    
            if (len(message) == 24):
                messageLength = int(message, 2) + 24
                key = key * (int(float(messageLength)/len(key)) + 1)
            
        sampleIndex += 1
        
        if (sampleIndex > 24):
            signalExtractingMessage.trigger.emit(float(len(message)) * 100 / messageLength)

                
    return message[24:]




