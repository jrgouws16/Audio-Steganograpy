#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 21:51:34 2019

@author: johan
"""

import dwtFirstPrinciples as dwt
import numpy as np

# Inverse of the binary_representation function of numpy
def binaryToInt(binaryString):
       
    if (binaryString[0] == '1'):
        return int(binaryString, 2)-(1<<len(binaryString))
    else:
        return int(binaryString, 2)

def getCapacity(coverSamples, LSBs):
      numBits       = 0
      numBlocks     = int(len(coverSamples)/512) 
      
      for blockNumber in range(0, numBlocks):
         
          subbandCoeff = []
      
          # Get the approximate coefficients and detail coefficients of the signal
          coefficiets = dwt.getLevelCoefficients(5, coverSamples[blockNumber*512:blockNumber*512 + 512])
          subbandCoeff.append(coefficiets[0])
          for i in range(0, len(coefficiets[1])):
              for j in range(0, len(coefficiets[1][i]), 16):
                  subbandCoeff.append(coefficiets[1][i][j:j + 16])
                  
          # Scale each subband by the maximum value inside the subband
          for i in range(0, len(subbandCoeff)):
              
              for j in range(0, len(subbandCoeff[i])):
                  
                    for k in range(25 - LSBs - 2, 25 - 2): 
                        numBits += 1
              
      return numBits - 28

# Function to encode a message within a audio file using the Haar DWT transform
# Takes in list of integer cover file samples
# Takes in a string of binary message bits
# Blocklenght is the length of the block on which the DWT Haar transform is 
# performed each time.
# Returns a list of integer stego file samples
def dwtScaleEncode(coverSamples, message, messageType, LSBs):
      samplesUsed = 0
      stegoSamples = []
      coverSamples = list(coverSamples)
      messageLength = len(message)
      numBlocks     = int(len(coverSamples)/512) 
      doBreak       = False  
      blockNumber   = 0    
      capacityWarning = False
      
      # Get the type of message
      # 0 is a textmessage and 1 is a wave message
      typeMessage = ""
    
      if (messageType == ".txt"):
          typeMessage = '0'
        
      elif (messageType == ".wav"):
          typeMessage = '1'
                          
      # Insert the type of message as the second element and the message length 
      # as the first element
      message = '{0:026b}'.format(messageLength) + typeMessage + message
      
      for blockNumber in range(0, numBlocks):
          # Reconstruct the coefficients into 32 subbands of 16 coeff each
          subbandCoeff = []
      
          # Get the approximate coefficients and detail coefficients of the signal
          coefficiets = dwt.getLevelCoefficients(5, coverSamples[blockNumber*512:blockNumber*512 + 512])
          subbandCoeff.append(coefficiets[0])
          for i in range(0, len(coefficiets[1])):
              for j in range(0, len(coefficiets[1][i]), 16):
                  subbandCoeff.append(coefficiets[1][i][j:j + 16])
                                    
          # Scale each subband by the maximum value inside the subband
          for i in range(0, len(subbandCoeff)):
              scalingValue = max(subbandCoeff[i])
              scalingValue = 100
              
              for j in range(0, len(subbandCoeff[i])):
                  samplesUsed += 1
                  
                  subbandCoeff[i][j] = subbandCoeff[i][j] * scalingValue  
                  intValue = int(subbandCoeff[i][j])
                  fraction = subbandCoeff[i][j] - intValue
                  
                  binaryWidth = 25
                  binaryValue = np.binary_repr(intValue, binaryWidth)
                  binaryValue = list(binaryValue)
                  
                 
                  for k in range(len(binaryValue) - LSBs - 2, len(binaryValue) - 2): 
                        
                        binaryValue[k] = message[0]
                        message = message[1:]
                        
                        if (len(message) == 0):
                            doBreak = True
                            break
                  
                  if (binaryValue[-1] == '1' and binaryValue[-2] == '1'):
                        binaryValue[-1] = '0'
                        binaryValue[-2] = '1'
                                          
                  if (binaryValue[-1] == '0' and binaryValue[-2] == '0'):
                        binaryValue[-1] = '0'
                        binaryValue[-2] = '1'
                    
                  binaryValue = "".join(binaryValue)          
     
                  if (scalingValue != 0):
                      subbandCoeff[i][j] = (binaryToInt(binaryValue) + fraction)/scalingValue
     
        
        
                  if (blockNumber == numBlocks - 1 and j == len(subbandCoeff[i]) - 1 and len(message)>0):
                      capacityWarning = True
        
        
                  if (doBreak == True):
                      break
              
              if (doBreak == True):
                  break
          
          for i in range(0, len(subbandCoeff[0])):
              coefficiets[0][i] = subbandCoeff[0][i]
          
            
          coefficiets[1][0] = subbandCoeff[1]
          coefficiets[1][1] = subbandCoeff[2]  + subbandCoeff[3]
          coefficiets[1][2] = subbandCoeff[4]  + subbandCoeff[5]  + subbandCoeff[6]  + subbandCoeff[7]
          coefficiets[1][3] = subbandCoeff[8]  + subbandCoeff[9]  + subbandCoeff[10] + subbandCoeff[11] + subbandCoeff[12] + subbandCoeff[13] + subbandCoeff[14] + subbandCoeff[15]                
          coefficiets[1][4] = subbandCoeff[16] + subbandCoeff[17] + subbandCoeff[18] + subbandCoeff[19] + subbandCoeff[20] + subbandCoeff[21] + subbandCoeff[22] + subbandCoeff[23] + subbandCoeff[24] + subbandCoeff[25] + subbandCoeff[26] + subbandCoeff[27] + subbandCoeff[28] + subbandCoeff[29] + subbandCoeff[30] + subbandCoeff[31]                
      
          stegoSamples += dwt.getLevelSignal(coefficiets[0], coefficiets[1])
          
          if (doBreak == True):
              break
                
      if (len(message) > 0):
          print("Message bits unembedded:", len(message))
        
      unaltered = coverSamples[-1*(len(coverSamples) - len(stegoSamples)):]
      
      return stegoSamples + unaltered, samplesUsed, capacityWarning

def dwtScaleDecode(stegoSamples, LSBs):
      message = ""
      stegoSamples = list(stegoSamples)
      
      # Embed the messagelength within the message
      messageLength = 0
      numBlocks     = int(len(stegoSamples)/512) 
      doBreak       = False  
      blockNumber   = 0     
      typeMessage   = "" 
      
      for blockNumber in range(0, numBlocks):
          
          # Reconstruct the coefficients into 32 subbands of 16 coeff each
          subbandCoeff = []
      
          # Get the approximate coefficients and detail coefficients of the signal
          coefficiets = dwt.getLevelCoefficients(5, stegoSamples[blockNumber*512:blockNumber*512 + 512])
          subbandCoeff.append(coefficiets[0])
          for i in range(0, len(coefficiets[1])):
              for j in range(0, len(coefficiets[1][i]), 16):
                  subbandCoeff.append(coefficiets[1][i][j:j + 16])
                  
          # Scale each subband by the maximum value inside the subband
          for i in range(0, len(subbandCoeff)):
              scalingValue = max(subbandCoeff[i])
              scalingValue = 100
              
              for j in range(0, len(subbandCoeff[i])):
                  
                  subbandCoeff[i][j] = subbandCoeff[i][j] * scalingValue  
                  intValue = int(subbandCoeff[i][j])                  
                  
                  binaryWidth = 25
                  
                  binaryValue = np.binary_repr(intValue, binaryWidth)
                  binaryValue = list(binaryValue)
                  

                  for k in range(len(binaryValue) - LSBs - 2, len(binaryValue) - 2):        
                        
                      message += binaryValue[k]
                        
                      if (len(message) == 27):
                          messageLength = int(message[0:26],2)
                                             
                          print(message[26])
                          
                          if (message[26] == '0'):
                              typeMessage = ".txt"
                                
                          else:
                              typeMessage = ".wav"
                                
                      if (len(message) == messageLength + 27):
                          doBreak = True
                          break
                                  
                  binaryValue = "".join(binaryValue)          

                  if (doBreak == True):
                      break
              
              if (doBreak == True):
                  break
          
          for i in range(0, len(subbandCoeff[0])):
              coefficiets[0][i] = subbandCoeff[0][i]
          
          
          if (doBreak == True):
              break
      
      return message[27:], typeMessage  




    
    
