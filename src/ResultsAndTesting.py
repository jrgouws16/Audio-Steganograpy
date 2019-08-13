# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 09:17:16 2019

@author: project
"""
import matplotlib.pyplot as plt
import numpy as np
import wave
import fileprocessing as fp
import geneticAlgorithm as GA
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
    totalOriginal = sum(originalSamples)**2
    difference = 0
    
    for i in range(0, len(originalSamples)):
        difference += (originalSamples[i] - embeddedSamples[i])**2 
    
    SNR = 10*np.log10(totalOriginal/difference)
    
    return SNR
    

###############################################################################
######################          Test the GA      ##############################              
###############################################################################
def testGA(song, key):

    cover = wave.open(song, mode='rb')
    print(cover.getframerate())

    
    
    coverSamples = fp.extractWaveSamples(cover)
    message = "Good\n"*len(coverSamples[0])
    secretMessage = fp.messageToBinary(message)
    originalCoverSamples = deepcopy(coverSamples[0])
    
    keyString = key
            
    # Convert ASCII to binary 
    binaryKey = fp.messageToBinary(keyString) 
    binaryKey = binaryKey * int((len(secretMessage) + float(len(secretMessage))/len(binaryKey)) )
    
    for i in range(0, len(coverSamples[0])):
        coverSamples[0][i] = "{0:016b}".format(coverSamples[0][i])

    secretMessage = "".join(map(str,secretMessage))
    

    stegoSamples = GA.insertMessage(coverSamples[0], binaryKey, "".join(map(str, secretMessage)))
    
    
    for i in range(0, len(stegoSamples)):
        stegoSamples[i] = int(stegoSamples[i], 2)
    
    print("SNR",getSNR(originalCoverSamples, stegoSamples))
    plotAmpDifference(originalCoverSamples, stegoSamples)
    
  

testGA('Media/song.wav', 'DDDDDDDDD')