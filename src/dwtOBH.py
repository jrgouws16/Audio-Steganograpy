# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:19:34 2019

@author: project
"""
import numpy as np
import dwtFirstPrinciples as dwt

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

def getCapacity(coverSamples, OBH, blockLength):
      numBits = -28
      
      # Get the approximate coefficients and detail coefficients of the signal
      coefficients = dwt.getCoefficients(coverSamples, blockLength)
      
      for block in range(0, len(coefficients[1])):
            for i in range(0, len(coefficients[1][block])):
                  
                  bits = calcPower(coefficients[1][block][i]) - OBH - 2
                  
                  if (bits < 1):
                        continue
                  
                  binCoeff = "{0:016b}".format(int(coefficients[1][block][i]))
                  binCoeff = list(binCoeff)
                  
                  for j in range(-1 * bits, 0):
                        numBits += 1
                        
      return numBits


# Function to encode a message within a audio file using the Haar DWT transform
# Takes in list of integer cover file samples
# Takes a binary bit string of the message
# OBH is the number of cover coefficient bits to keep
# Blocklenght is the length of the block on which the DWT Haar transform is 
# performed each time.
# Returns a list of integer stego file samples
def dwtHaarEncode(coverSamples, message, OBH, blockLength, messageType):
      samplesUsed = 0 
      doBreak     = False
      originalMessageLen = len(message)
      progress = 0
      
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
      
      for block in range(0, len(coefficients[1])):
            
            if (int(100 - 100*len(message)/originalMessageLen)>progress):
                  progress = int(100 - 100*len(message)/originalMessageLen)
                  print(progress, end =" ")
            
            for i in range(0, len(coefficients[1][block])):
                  
                  bits = calcPower(coefficients[1][block][i]) - OBH - 2
                  samplesUsed += 2
                  
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

                  coefficients[1][block][i] = int(binCoeff,2)
                  
                  if (doBreak == True):
                        break
            
            if (doBreak == True):
                  break
                     
      # Reconstruct the signal
      stegoSamples = []
      for i in range(0, len(coefficients[1])):
          temp = dwt.getSignal(coefficients[0][i], coefficients[1][i])
          temp = list(map(float, temp))
          stegoSamples += temp
          
      unaltered = coverSamples[-1*(len(coverSamples) - len(stegoSamples)):]    
          
      return stegoSamples + unaltered, samplesUsed

# Function to decode a message from a stego audio file using the Haar DWT transform
# Takes in list of integer stego file samples
# OBH is the number of cover coefficient bits to keep
# Blocklenght is the length of the block on which the DWT Haar transform is 
# performed each time.
# Returns a binary bit stream of the message that was extracted and the type of message embedded
def dwtHaarDecode(stegoSamples, OBH, blockLength):
      # Get the approximate coefficients and detail coefficients of the signal
      coefficients = dwt.getCoefficients(stegoSamples, blockLength)
      
      # Embed the messagelength within the message
      messageLength = 0
      typeMessage = ''
      message = ''
      doBreak = False
      
      for block in range(0, len(coefficients[1])):
                  
            for i in range(0, len(coefficients[1][block])):
                  
                  bits = calcPower(coefficients[1][block][i]) - OBH - 2
                  if (bits < 0):
                        continue
                  binCoeff = "{0:016b}".format(int(coefficients[1][block][i]))
                  binCoeff = list(binCoeff)
                  
                  for j in range(-1 * bits, 0):
                        message += binCoeff[j - 2]
                                         
                        if (len(message) == messageLength + 28 and messageLength != 0):
                              doBreak = True
                              break
                        
                        if (len(message) == 28):
                              messageLength = int(message[0:26], 2)
                             
                              if (message[26:28] == '00'):
                                    typeMessage = '.txt'
    
                              elif (message[26:28] == '01'):
                                    typeMessage = '.wav'
                                         
                  
                  if (doBreak == True):
                        break
            
            if (doBreak == True):
                  break

      return message[28:], typeMessage


