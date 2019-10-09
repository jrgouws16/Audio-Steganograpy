# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 11:23:30 2019

@author: project
"""

import numpy as np
import dwtFirstPrinciples as dwt

# Function calculating the p value required to determine 
# number of bits to embed
def calcPower(coefficient):
    p = 0
    
    coefficient = np.abs(coefficient)
          
    for i in range(0,25):
        if ((2 ** i) > coefficient):
            p = i - 1
            break
        
    if (p == -1):
        p = 0
        
    return p

# Inverse of the binary_representation function of numpy
def binaryToInt(binaryString):
       
    if (binaryString[0] == '1'):
        return int(binaryString, 2)-(1<<len(binaryString))
    else:
        return int(binaryString, 2)
    
# Function to encode a message within a audio file using the Haar DWT transform
# Takes in list of integer cover file samples
# Takes in a string of binary message bits
# Blocklenght is the length of the block on which the DWT Haar transform is 
# performed each time.
# Returns a list of integer stego file samples
def dwtHybridEncode(coverSamples, message, messageType, OBH):
      samplesUsed = 0
      stegoSamples = []
      coverSamples = list(coverSamples)
      messageLength = len(message)
      numBlocks     = int(len(coverSamples)/512) 
      doBreak       = False  
      blockNumber   = 0     

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
                  
                  bits = calcPower(subbandCoeff[i][j]) - OBH
                  fraction = subbandCoeff[i][j] - intValue
                  
                  binaryWidth = 25
                  binaryValue = np.binary_repr(intValue, binaryWidth)
                  binaryValue = list(binaryValue)
                  
                  for k in range(len(binaryValue) - bits, len(binaryValue) - 3): 
                        binaryValue[k] = message[0]
                        message = message[1:]
                        
                        if (len(message) == 0):
                            doBreak = True
                            break

                  binaryValue[-1] = '0'
                  binaryValue[-2] = '0'
                  binaryValue[-3] = '1'
                                          
                  binaryValue = "".join(binaryValue)          
     
                  if (scalingValue != 0):
                      subbandCoeff[i][j] = (binaryToInt(binaryValue) + fraction)/scalingValue
     
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
      
      return stegoSamples + unaltered, samplesUsed

def dwtHybridDecode(stegoSamples, OBH):
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
                  bits = calcPower(subbandCoeff[i][j]) - OBH
                  intValue = int(subbandCoeff[i][j])                  
                  
                  binaryWidth = 25
                  
                  binaryValue = np.binary_repr(intValue, binaryWidth)
                  binaryValue = list(binaryValue)
                  

                  for k in range(len(binaryValue) - bits, len(binaryValue) - 3):
                        
                      message += binaryValue[k]
                        
                      if (len(message) == 27):
                          messageLength = int(message[0:26],2)
                         
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
