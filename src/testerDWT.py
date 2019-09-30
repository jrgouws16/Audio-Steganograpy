# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 17:19:35 2019

@author: Johan Gouws
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:19:34 2019

@author: project
"""

# https://dsp.stackexchange.com/questions/45758/programming-the-idwt-for-image-processing
# https://dsp.stackexchange.com/questions/47437/discrete-wavelet-transform-visualizing-relation-between-decomposed-detail-coef
# https://dsp.stackexchange.com/questions/48138/how-to-implement-a-filter-associated-to-a-specific-wavelet

import numpy as np
import math
import dwtFirstPrinciples as dwt
import fileprocessing as fp
import scipy.io.wavfile as scWave
from copy import deepcopy

# Function calculating the p value required to determine 
# number of bits to embed
def calcPower(coefficient):
    p = 0
    
    coefficient = np.abs(coefficient)
          
    for i in range(0,17):
        if ((2 ** i) > coefficient):
            p = i - 1
            break
        
    if (p == -1):
        p = 0
        
    return p

# Function to encode a message within a audio file using the Haar DWT transform
# Takes in list of integer cover file samples
# Takes a binary bit string of the message
# OBH is the number of cover coefficient bits to keep
# Blocklenght is the length of the block on which the DWT Haar transform is 
# performed each time.
# Returns a list of integer stego file samples
def dwtHaarEncode(coverSamples, message, OBH, blockLength, messageType):
       
      doBreak = False
      
      # Get the approximate coefficients and detail coefficients of the signal
      coefficients = dwt.getCoefficients(coverSamples, blockLength)
      
      # Embed the messagelength within the message
      messageLength = len(message)
      messageLength = '{0:026b}'.format(messageLength)
      
      typeMessage = '{0:02b}'.format(0)
    
      if (messageType == ".txt"):
          typeMessage = '{0:02b}'.format(0)
        
      elif (messageType == ".wav"):
          typeMessage = '{0:02b}'.format(1)
                
      message = messageLength + typeMessage + message
      count = 10
      
      for block in range(0, len(coefficients[1])):
                  
            for i in range(0, len(coefficients[1][block])):
                  orgy = coefficients[1][block][i]
                  bits = calcPower(coefficients[1][block][i]) - OBH - 2
                  if (bits < 1):
                        continue
                  
                  binCoeff = "{0:016b}".format(int(coefficients[1][block][i]))
                  binCoeff = list(binCoeff)
                  binCoeff[-1] = '0'
                  binCoeff[-2] = '1'
                  for j in range(-1 * bits, 0):
                        binCoeff[j - 2] = message[0]
                        message = message[1:]
                        
                        if (len(message) == 0):
                              doBreak = True
                              break
                                          
                  binCoeff = "".join(binCoeff)

                  if (count > 0 ):
                        print(binCoeff)
                        count -=1
                  
                  if (calcPower(int(binCoeff,2)) - OBH - 2 != bits):
                        print(calcPower(int(binCoeff,2)) - OBH - 2, bits, orgy, int(binCoeff,2))

                  
                  if (int(binCoeff,2) < 0):
                        coefficients[1][block][i] = int(binCoeff,2)
                        
                  else:
                        coefficients[1][block][i] = int(binCoeff,2)
                  
                  if (doBreak == True):
                        break
            
            if (doBreak == True):
                  break
                  
      originalCoeff = deepcopy(coefficients)
   
      # Reconstruct the signal
      stegoSamples = []
      for i in range(0, len(coefficients[1])):
          temp = dwt.getSignal(coefficients[0][i], coefficients[1][i])
          temp = list(map(float, temp))
          stegoSamples += temp
          
      unaltered = coverSamples[-1*(len(coverSamples) - len(stegoSamples)):]    
          
      return stegoSamples + unaltered, originalCoeff

def dwtHaarDecode(stegoSamples, blockLength):
      print("Decoding")
      # Get the approximate coefficients and detail coefficients of the signal
      coefficients = dwt.getCoefficients(stegoSamples, blockLength)
      
      # Embed the messagelength within the message
      messageLength = 0
      typeMessage = ''
      message = ''
      doBreak = False
      count = 10
      for block in range(0, len(coefficients[1])):
                  
            for i in range(0, len(coefficients[1][block])):
                  
                  bits = calcPower(coefficients[1][block][i]) - OBH - 2
                  if (bits < 0):
                        continue
                  binCoeff = "{0:016b}".format(int(coefficients[1][block][i]))
                  
                  if (count > 0):
                        print(binCoeff)
                        count-=1
                  binCoeff = list(binCoeff)
                  
                  for j in range(-1 * bits, 0):
                        message += binCoeff[j - 2]
                                         
                        if (len(message) == messageLength + 28 and messageLength != 0):
                              doBreak = True
                              break
                        
                        if (len(message) == 28):
                              messageLength = int(message[0:26], 2)
                              print(messageLength)
                             
                              if (message[26:28] == '00'):
                                    typeMessage = '.txt'
    
                              elif (message[26:28] == '01'):
                                    typeMessage = '.wav'
                                         
                  
                  if (doBreak == True):
                        break
            
            if (doBreak == True):
                  break

      return message[28:], typeMessage, coefficients

OBH = 4
print("Extracting wave samples")
samplesOne, samplesTwo, rate = fp.getWaveSamples("Media/song.wav")

print("Extracting message samples")
message = ""
message = fp.getMessageBits("Media/opera.wav")
message = "".join(list(map(str, message)))
print(len(message))           
print("Encoding")
stegoSamples, coeffOne = dwtHaarEncode(samplesOne, message, OBH, 4096, ".wav")
print("Writing to stego file")  
  
# Write to the stego audio file in wave format and close the song
minStego = np.abs(min(stegoSamples))
maxStego = max(stegoSamples)

stegoSamples = np.asarray(stegoSamples, dtype=np.float32, order = 'C')/max([minStego,maxStego])
origStego = deepcopy(stegoSamples)
#print(stegoSamples.dtype)
#stegoSamples = stegoSamples.astype(np.float32, order='C')
scWave.write('Media/Koekies3.wav', rate, stegoSamples)
  
print("Reading from stego")
  
# Extract the wave samples from the host signal
samplesOneStego, samplesTwoStego, rate = fp.getWaveSamples("Media/Koekies3.wav")
samplesOneStego = np.asarray(samplesOneStego, dtype=np.float32, order = 'C')*max([minStego,maxStego])

message, fileType, coeffTwo = dwtHaarDecode(samplesOneStego, 4096)
fp.writeMessageBitsToFile(message, 'Pannekoekies4.wav')

allDiffs = []
for blocks in range(0, len(coeffOne[1])):
      for samples in range(0, len(coeffOne[1][blocks])):
            allDiffs.append(np.abs(int(coeffOne[1][blocks][samples]) - int(coeffTwo[1][blocks][samples])))
            
print(max(allDiffs))





