#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 19:26:32 2019

@author: johan
"""

import dwtFirstPrinciples as dwt
import numpy as np

# Function to get the number of 1's in the length of the message
# Input: integer of the length of the message
# Output: the number of 1's in the binary representation of the length of the message        
def getCount(messageLength):
    if(messageLength > 4294967295):
        print("Error, because the message is too long")
    
    binaryMessage = np.binary_repr(messageLength, 32)
    count = 0
    
    for i in binaryMessage:
        if (i == '1'):
            count += 1
            
    return count

def school_round(a_in,n_in):
    if (a_in * 10 ** (n_in + 1)) % 10 == 5:
        return round(a_in + 1 / 10 ** (n_in + 1), n_in)
    else:
        return round(a_in, n_in)

def getCapacity(coverSamples, blockLength):
      bits = -28
      
      # Get the approximate coefficients and detail coefficients of the signal
      coefficiets = dwt.getCoefficients(coverSamples, blockLength)
      
      for blockNumber in range(0, len(coefficiets[1])):
          for i in range(0, len(coefficiets[1][blockNumber])):
              bits += 8
              
      return bits - 50

# Function to encode a message within a audio file using the Haar DWT transform
# Takes in list of integer cover file samples
# Takes a integer list of ascii values as the message
# Blocklenght is the length of the block on which the DWT Haar transform is 
# performed each time.
# Returns a list of integer stego file samples
def dwtEncryptEncode(coverSamples, message, blockLength, messageType):
      samplesUsed = 0
      print(len(message))
      capacityWarning = False
      
      # Embed the messagelength within the message
      messageLength = len(message)
      
      # Get the count. Number of 1's in the binary represenetation of the length 
      # of the message
      count = getCount(messageLength)
      doBreak = False  
      blockNumber = 0     
      
      # Convert the message to the ASCII representation as a integer list
      message = list(map(ord,message))
      
      # Subtract the count from every ASCII character of the message
      for i in range(0, messageLength):
          message[i] = message[i] - count
                
      
      # Divide by 10000 to get four decimal digits
      message = list(np.asarray(message)/1000)

      # Get the approximate coefficients and detail coefficients of the signal
      coefficiets = dwt.getCoefficients(coverSamples, blockLength)
      
      # Get the type of message
      # 0 is a textmessage and 1 is a wave message
      typeMessage = 0
    
    
     
      if (messageType == ".txt"):
          typeMessage = 0.5000
        
      elif (messageType == ".wav"):
          typeMessage = 0.1000
      
      # Insert the type of message as the second element and the message length 
      # as the first element
      message.insert(0, typeMessage)
      message.insert(0, messageLength)
           
      for blockNumber in range(0, len(coefficiets[1])):
            
          samplesUsed = (blockNumber + 1) * blockLength
            
          for i in range(0, len(coefficiets[1][blockNumber])):

              # Replace the coefficient by the encrypted ascii char
              
              coefficiets[1][blockNumber][i] = int(coefficiets[1][blockNumber][i]/10)
              if (blockNumber == 0 and i == 0):
                  coefficiets[1][blockNumber][i] = message[0]/1000000
                  
              elif (coefficiets[1][blockNumber][i] > 0):
                  coefficiets[1][blockNumber][i] += message[0]
                  
              else:    
                  coefficiets[1][blockNumber][i] -= message[0] 
              
              coefficiets[1][blockNumber][i] = coefficiets[1][blockNumber][i] * 10

              message = message[1:]
              
              if (blockNumber == len(coefficiets[1]) - 1 and i == len(coefficiets[1][blockNumber]) - 1 and len(message) > 0):
                  capacityWarning = True
              
              # If the message is embedded, break
              if (len(message) == 0):
                  doBreak = True
                  break
              
          if (doBreak == True):
              break
              
      # Reconstruct the signal
      stegoSamples = []
      for i in range(0, len(coefficiets[1])):
          temp = dwt.getSignal(coefficiets[0][i], coefficiets[1][i])
          temp = list(map(float, temp))
          stegoSamples += temp
      
      unaltered = coverSamples[-1*(len(coverSamples) - len(stegoSamples)):]

      return stegoSamples + unaltered, samplesUsed, capacityWarning

def dwtEncryptDecode(stegoSamples, blockLength):
      # Get the approximate coefficients and detail coefficients of the signal
      newCoeff = dwt.getCoefficients(stegoSamples, blockLength) 
      extractedLength = 0
      returnList = []
      extractMessage = []
      fileType = ''
      blockNumber = 0      
      doBreak = 0
      while(1):
          for i in range(0, len(newCoeff[1][blockNumber])):    
              
              newCoeff[1][blockNumber][i] = newCoeff[1][blockNumber][i] / 10 
              if (blockNumber == 0 and i == 0):  
                    extractMessage.append(int(np.abs(school_round(newCoeff[1][blockNumber][i]*1000000,0))))
                    returnList.append(int(np.abs(school_round(newCoeff[1][blockNumber][i]*1000000,0))))
              else:
                    extractMessage.append(np.abs(school_round(newCoeff[1][blockNumber][i] - int(newCoeff[1][blockNumber][i]),3)))
                    returnList.append(np.abs(school_round(newCoeff[1][blockNumber][i] - int(newCoeff[1][blockNumber][i]),3)))
                    
              
              # Interpret the message length and the message type  
              if (len(extractMessage) == 2):
                  
                  extractedLength = int(school_round(extractMessage[0],0))
                  if (extractMessage[1] == 0.5000):
                      fileType = '.txt'

                  elif (extractMessage[1] == 0.1000):
                      fileType = '.wav'
                  
              # If the full message is extracted, break the while loop
              elif (len(extractMessage) == extractedLength + 2):
                  extractMessage = extractMessage[2:]
                  
                  doBreak = 1
                  break
               
          blockNumber += 1
          if(doBreak == 1):
              break
      
      # Get the count to decrypt the message  
      count = getCount(extractedLength)  
      
      # Add the count and scale the message  
      for i in range(0, len(extractMessage)):
          extractMessage[i] = int(extractMessage[i] * 1000 + count)
          
      # Map the ASCII value to the character version  
      extractMessage = "".join(list(map(chr, extractMessage)))
      
      
      return extractMessage, fileType

