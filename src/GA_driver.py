# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 14:10:15 2019

@author: project
"""

import geneticAlgorithm as GA
import numpy as np
import random
import ResultsAndTesting as RT
from copy import deepcopy
import scipy.io.wavfile as scWave
import fileprocessing as fp

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
        print("Failed at test", numberTests)
        print("Message", message)
        print("Extract", extractedMsg)
        print("Error")
        break
    
    elif (numberTests == 999):
        print("Extensive testing: Passed all the tests")
  

print("##################################################")
print("#        Hiding opera.wav into song.wav          #")
print("##################################################")

# Function to extract the message from the stego file making use of 
# Genetic Algorithm
def GA_decoding(stegoSamples, key):
    
    
    
    # Convert integer samples to binary samples
    for i in range(0, len(stegoSamples)):
                
        stegoSamples[i] = "{0:016b}".format(int(stegoSamples[i]))
        
    # Extract secret message
    secretMessage, fileType = GA.extractMessage(stegoSamples, key)
        
    return secretMessage, fileType

# Function for encoding using the standard LSB encoding algorithm
def GA_encoding(coverSamples, secretMessage, key, frameRate, fileType):
        # Deepcopy for calculating the SNR
        originalCoverSamples = deepcopy(coverSamples[0])

        for i in range(0, len(coverSamples[0])):
            coverSamples[0][i] = "{0:016b}".format(coverSamples[0][i])

        secretMessage = "".join(map(str,secretMessage))
    
        # Provide first audio channel samples and message samples to encode 
        stegoSamples, samplesUsed, bitsInserted = GA.insertMessage(coverSamples[0], key, "".join(map(str, secretMessage)), fileType)
        
        # Convert the binary audio samples to decimal samples
        for i in range(0, len(stegoSamples)):
            stegoSamples[i] = int(stegoSamples[i], 2)
        
        # Get the characteristics of the stego file
        infoMessage = "Embedded " + str(bitsInserted) + " bits into " + str(samplesUsed) + " samples."
        infoMessage += "\nSNR of " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] ), 2))
        infoMessage += ".\nCapacity of " + str(RT.getCapacity(secretMessage, samplesUsed, frameRate)) + " kbps."       

        return stegoSamples         
      
      
secretMessage = ""

# Get the audio samples in integer form converted to binary
print("Getting message samples")
intSamples = fp.extractWaveMessage("Media/opera.wav")

# Convert to integer list of bits for embedding
secretMessage = "".join(intSamples[0])
secretMessage = list(map(int, list(secretMessage)))

print("Getting cover samples")
coverSamplesOne, coverSamplesTwo, rate = fp.getWaveSamples("Media/song.wav")

for i in range(0, len(coverSamplesOne)):
    if (coverSamplesOne[i] <= -32768):       
            coverSamplesOne[i] += 1
            
coverSamples = [coverSamplesOne, coverSamplesTwo]

# Convert ASCII to binary 
binaryKey = fp.messageToBinary("xrdpkd8x")
binaryKey = binaryKey * int((len(secretMessage) + float(len(secretMessage))/len(binaryKey)) )


print("Encoding")
stegoSamples = GA_encoding(coverSamples, secretMessage, binaryKey, rate, fileType)

beforeWritingSamples = deepcopy(stegoSamples)

print("Writing to stego file")
# Write to the stego audio file in wave format and close the song
stegoSamples = np.asarray(stegoSamples, dtype=np.float32, order = 'C')/ 32768.0
scWave.write("myGAtestingstego.wav", rate, stegoSamples)
      

print("Reading from stego file")
stegoSamplesOne, stegoSamplesTwo, rate = fp.getWaveSamples("myGAtestingstego.wav")
stegoSamples = np.asarray(stegoSamplesOne, dtype=np.float32, order = 'C') * 32768.0
afterWritingSamples = deepcopy(stegoSamples)
# Get the secret message
print("Decoding")
secretMessageExtract, fileType = GA_decoding(list(stegoSamples), binaryKey)
               
print("Writing to extracted message file")
fp.writeWaveMessageToFile(secretMessageExtract, "extractedOpera.wav")

startPrinting = 0 
for i in range(0, len(secretMessageExtract)):
   if (str(secretMessageExtract[i]) != str(secretMessage[i])):
       startPrinting = 100
       
   if (startPrinting > 0):
       print(str(secretMessageExtract[i]), str(secretMessage[i]))
       startPrinting-=1
       
   if (startPrinting == 1):
       break
      
      
      
      
      
      
      
      
      
      
      
      
      
      