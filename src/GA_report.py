# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 23:26:31 2019

@author: Johan Gouws
"""
import ResultsAndTesting as RT
import geneticAlgorithm as GA
import fileprocessing as fp
import numpy as np
import matplotlib.pyplot as plt

import scipy.io.wavfile as scWave
from copy import deepcopy
import time
import os
import AES



def GA_encoding(coverSamples, secretMessage, key, frameRate, fileType):
        # Deepcopy for calculating the SNR
        originalCoverSamples = deepcopy(coverSamples[0])

        for i in range(0, len(coverSamples[0])):
            coverSamples[0][i] = "{0:016b}".format(coverSamples[0][i])

        secretMessage = "".join(map(str,secretMessage))
    
        # Provide first audio channel samples and message samples to encode 
        stegoSamples, samplesUsed, bitsInserted, capacityWarning = GA.insertMessage(coverSamples[0], key, "".join(map(str, secretMessage)), fileType)
        
        # Convert the binary audio samples to decimal samples
        for i in range(0, len(stegoSamples)):
            stegoSamples[i] = int(stegoSamples[i], 2)
        
            if (stegoSamples[i] < -32768):
                stegoSamples[i] = -32768
            
            if (stegoSamples[i] > 32767):
                stegoSamples[i] = 32767
                   
        # Get the characteristics of the stego file
        SNR = RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed])
        capacity = RT.getCapacity(secretMessage, samplesUsed, frameRate)
                
        return stegoSamples, capacity, SNR, capacityWarning, samplesUsed
  
# Function to extract the message from the stego file making use of 
# Genetic Algorithm
def GA_decoding(stegoSamples, key):
    
    # Convert integer samples to binary samples
    for i in range(0, len(stegoSamples)):
                
        stegoSamples[i] = "{0:016b}".format(int(stegoSamples[i]))
        
    # Extract secret message
    secretMessage, fileType = GA.extractMessage(stegoSamples, key)
        
    return secretMessage, fileType

allPaths = ['C:/Users/Johan Gouws/Desktop/GenresDatabase/Alternative',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Blues',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Electronic',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Jazz',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Pop',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Rock']

numSongsPerGenre = 50
textMessage = True

SNRAlt = 0
SNRBlu = 0
SNREle = 0
SNRJzz = 0
SNRPop = 0
SNRRoc = 0

CapAlt = 0
CapBlu = 0
CapEle = 0
CapJzz = 0
CapPop = 0
CapRoc = 0

SamAlt = 0
SamBlu = 0
SamEle = 0
SamJzz = 0
SamPop = 0
SamRoc = 0

counter = numSongsPerGenre * 6

for path in allPaths:
      coverFiles = []
          
      for r, d, f in os.walk(path):
        for file in f:
            if '.wav' in file:
                coverFiles.append(os.path.join(r, file))


      coverFiles = coverFiles[0:numSongsPerGenre]
      if (textMessage == True):
            
            for t in coverFiles:
                  AESkeyEncode = "THIS_IS_THE_KEY_USED_FOR_AES_ENCRYPTION"
                      
                  stegoSamples = []
                    
                  # Get the string representation of the key in ASCII
                  keyString = "THIS_IS_THE_KEY_USED_FOR_GA_ENCRYPTION"
                  
                  coverSamplesOne, coverSamplesTwo, rate = fp.getWaveSamples(t)
                    
                  for i in range(0, len(coverSamplesOne)):
                      if (coverSamplesOne[i] <= -32768):       
                              coverSamplesOne[i] += 1
                    
                  coverSamples = [coverSamplesOne, coverSamplesTwo]
                  
                  secretMessage = ""
            
                  secretMessage = fp.getMessageBits('C:/Users/Johan Gouws/Desktop/Audio-Steganograpy/src/Media/text.txt')
                  secretMessage = list(map(str, secretMessage))
                  secretMessage = ''.join(secretMessage)
                  secretMessage = AES.encryptBinaryString(secretMessage, AESkeyEncode)
                  secretMessage = list(map(int, list(secretMessage)))
                    
                  # Convert ASCII to binary 
                  binaryKey = fp.messageToBinary(keyString)
                  binaryKey = binaryKey * int((len(secretMessage) + float(len(secretMessage))/len(binaryKey)) )
                      
                  stegoSamples, capacity, SNR, capacityWarning, samplesUsed = GA_encoding(coverSamples, secretMessage, binaryKey, rate, '.txt')
                  
                  print(counter, end=" ")
                  counter -= 1                  
                  
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Alternative'):
                       SNRAlt += SNR
                       CapAlt += capacity
                       SamAlt += samplesUsed
                       
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Blues'):
                       SNRBlu += SNR
                       CapBlu += capacity
                       SamBlu += samplesUsed
                       
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Electronic'):
                       SNREle += SNR
                       CapEle += capacity
                       SamEle += samplesUsed
                       
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Jazz'):
                       SNRJzz += SNR
                       CapJzz += capacity
                       SamJzz += samplesUsed
                       
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Pop'):
                       SNRPop += SNR
                       CapPop += capacity
                       SamPop += samplesUsed
                       
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Rock'):
                       SNRRoc += SNR
                       CapRoc += capacity
                       SamRoc += samplesUsed

                       
                       
x = ['Alternative','Blues','Electronic','Jazz','Pop','Rock']
x = np.asarray(x)       
              
plt.figure(13)
plt.ylabel('SNR (dB)')
plt.plot(x, [SNRAlt/numSongsPerGenre,SNRBlu/numSongsPerGenre,SNREle/numSongsPerGenre,SNRJzz/numSongsPerGenre,SNRPop/numSongsPerGenre,SNRRoc/numSongsPerGenre])
plt.figure(14)
plt.ylabel('Capacity (bits per 16 bit cover sample)')
plt.plot(x, [CapAlt*1000/44100/numSongsPerGenre,CapBlu*1000/44100/numSongsPerGenre,CapEle*1000/44100/numSongsPerGenre,CapJzz*1000/44100/numSongsPerGenre,CapPop*1000/44100/numSongsPerGenre,CapRoc*1000/44100/numSongsPerGenre])
plt.figure(15)
plt.ylabel('Samples Used')
plt.plot(x, [SamAlt/numSongsPerGenre,SamBlu/numSongsPerGenre,SamEle/numSongsPerGenre,SamJzz/numSongsPerGenre,SamPop/numSongsPerGenre,SamRoc/numSongsPerGenre])
            

