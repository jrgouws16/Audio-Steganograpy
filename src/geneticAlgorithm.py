# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 14:10:15 2019

@author: project
"""

# Function that takes a 16-bit audio sample and generates 5 chromosomes
# of the sample, by inserting the bit in LSB positions 4 - 8
def generatePopulation(sample, bit):
    
    population = []
    
    for i in range(8, 13):
        addSample = list(sample)
        addSample[i] = bit
        population.append("".join(addSample))
        
    return population

# Performs crossover operation for the sample with 16-bit samples of one
# Ones is inserted in position start to position stop in the sample   
def crossOverOnes(start, stop, sample):
    
    for i in range(start, stop):
        sample[i] = '1'
   
    return sample

# Performs crossover operation for the sample with 16-bit samples of zero
# Zeros is inserted in position start to position stop in the sample   
def crossOverZeros(start, stop, sample):
    
    for i in range(start, stop):
        sample[i] = '0'
   
    return sample

# Function that takes a current population and generates a better population
def generateNextGeneration(population):
    
    # Convert population into a list of lists, in order to do bit operations
    for i in range(0, len(population)):
        population[i] = list(population[i])
        
    # i is the embedding position, corresponding with the first individual 
    # in the population
    i = -4
    
    for j in range(0, 5):
        
        # If message bit (Ei) is zero
        if (population[0][8] == '0'):
            
            # If data bit at i is zero, do nothing
            if(population[j][i] == '0'):
                continue
            
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
                    population[j] = crossOverOnes(i - 1, -3, population[j])
                    
                # Put 0 at position i and perform crossover from i-1 to 3 
                # with 1...11111 string    
                else:
                    population[j][i] = '0'
                    population[j] = crossOverOnes(i - 1, -3, population[j])
                    
                    # if data bit at i + 1 is 0, then perform mutation at 
                    # position i + 1 and crossover operation at position from 
                    # i-1 to 3 with 000.00000 string
                    if (population[j][i - 1] == '0'):
                        population[j][i - 1] = '1'
                        population[j] = crossOverZeros(i - 1, -3, population[j])
            
        # If the message bit (Ei) is one    
        else:
            # If data bit at i is one, do nothing
            if(population[j][i] == '1'):
                continue
            
            else:
                # If position bit of i is at -4, put 0 at i
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
                    population[j] = crossOverZeros(i - 1, -3, population[j])
                    
                # Put 1 at position i and perform crossover from i-1 to 3 
                # with 0...000000 string    
                else:
                    population[j][i] = '1'
                    population[j] = crossOverZeros(i - 1, -3, population[j])
                    
                    # if data bit at i + 1 is 1, then perform mutation at 
                    # position i + 1 and crossover operation at position from 
                    # i-1 to 3 with 1111.1 string
                    if (population[j][i - 1] == '1'):
                        population[j][i - 1] = '0'
                        population[j] = crossOverOnes(i - 1, -3, population[j])
            
        i = i - 1
            
    
    for i in range(0, len(population)):
        population[i] = "".join(population[i])
    
    return population

