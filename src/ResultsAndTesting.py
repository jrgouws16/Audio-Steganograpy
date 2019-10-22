# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 09:17:16 2019

@author: project
"""
import math
import matplotlib.pyplot as plt
import numpy as np
import wave
import fileprocessing as fp
import geneticAlgorithm as GA
import random
from copy import deepcopy

# Takes the sequence of original audio samples and the stego samples and 
# plots the amplitude difference between the samples for a snippet of the 
# audio file.
def plotAmpDifference(originalSamples, stegoSamples):
    x = np.arange(49,100,1)
    y = np.abs(originalSamples[49:100])
    plt.plot(x, y, '-go', color='blue', linewidth=2, markersize=8, label = 'original Signal')
    y = np.abs(stegoSamples[49:100])
    plt.plot(x, y, 'go', color='red', linewidth=2, markersize=4, label = 'stegoLabel')
    plt.legend()

# Provide all the samples that were embedded and the original samples.
# Do not include samples where not message bits were hidden within
def getSNR(originalSamples, embeddedSamples):
    
    totalOriginal = math.pow(sum(originalSamples), 2)
    difference = 0
    
    for i in range(0, len(originalSamples)):
        difference += (originalSamples[i] - embeddedSamples[i])**2 
        
    SNR = 10*np.log10(totalOriginal/difference)
    
    return SNR
    
# Gives a range of 0 - 1, where 1 is ideal
def getSPCC(originalSamples, stegoSamples):
      avgOriginal = sum(originalSamples)/len(originalSamples)
      avgStego = sum(stegoSamples)/len(stegoSamples)
      
      
      denominator = 0
      squareOne   = 0
      squareTwo   = 0
      
      total = 0
      
      for i in range(0, len(originalSamples)):
            squareOne += (originalSamples[i] - avgOriginal)**2
            squareTwo += (stegoSamples[i] - avgStego)**2
                      
      squareOne = math.sqrt(squareOne)
      squareTwo = math.sqrt(squareTwo)
      denominator = squareOne*squareTwo
      
      for i in range(0, len(originalSamples)):
            total += ((originalSamples[i] - avgOriginal)*(stegoSamples[i] - avgStego))
            
      total = total/denominator
            
      return total**2
      


# Average square of the differences between the input and the output signal
def getMSE(orig, steg):
      total = 0
      
      for i in range(0, len(orig)):
            total += (orig[i] - steg[i])**2
            
      return total/len(orig)

# Measures the maximum SNR of a given signal
def getPSNR(orig, steg):
      return 10*np.log10((2**16-1)**2/getMSE(orig,steg))
      
def getPRD(orig, steg):
      numerator   = 0
      denominator = sum(orig)
      
      for i in range(0, len(orig)):
            numerator += (orig[i] - steg[i])**2
            
      return math.sqrt(numerator/denominator)

x = [5,3,12,4,9,10,11,12,13,14,15,16]
y = [5,3,12,3,8,9,10,11,12,13,14,15]

#print(getSNR(x,y))
#print(getSPCC(x,y))
#print(getMSE(x,y))
#print(getPSNR(x,y))
#print(getPRD(x,y))
      
      
# Give only the message bits that were encoded as well as the amount of samples 
# used to embed the message. The framerate is from the wave file 
def getCapacity(secretMessage, samplesUsed, frameRate):
      return (len(secretMessage)/(samplesUsed/frameRate))/1000

###############################################################################
######################          Test the GA      ##############################              
###############################################################################
def testGA(song, key):
    cover = wave.open(song, mode='rb')
    coverSamples = fp.extractWaveSamples(cover)
    
    message = "G" * int(16777200/8)
    secretMessage = fp.messageToBinary(message)
    originalCoverSamples = deepcopy(coverSamples[0])
    keyString = key  
    binaryKey = fp.messageToBinary(keyString) 
    binaryKey = binaryKey * int((len(secretMessage) + float(len(secretMessage))/len(binaryKey)) )
    
    for i in range(0, len(coverSamples[0])):
        coverSamples[0][i] = "{0:016b}".format(coverSamples[0][i])

    secretMessage = "".join(map(str,secretMessage))
    stegoSamples, samplesUsed, bitsInserted, capacityWarning = GA.insertMessage(coverSamples[0], binaryKey, "".join(map(str, secretMessage)))
        
    print("Message bits inserted", bitsInserted)
    print("Samples used", samplesUsed)
    
    for i in range(0, len(stegoSamples)):
        stegoSamples[i] = int(stegoSamples[i], 2)
    
    print("SNR",getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed]))
    plotAmpDifference(originalCoverSamples, stegoSamples)




#testGA('Media/opera.wav', 'DDDDDDDDD')