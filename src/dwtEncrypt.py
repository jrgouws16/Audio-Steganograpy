#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 19:26:32 2019

@author: johan
"""

import dwtFirstPrinciples as dwt
import numpy as np

def school_round(a_in,n_in):
    if (a_in * 10 ** (n_in + 1)) % 10 == 5:
        return round(a_in + 1 / 10 ** (n_in + 1), n_in)
    else:
        return round(a_in, n_in)

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

# Function to encode a message within a audio file using the Haar DWT transform
# Takes in list of integer cover file samples
# Takes a integer list of ascii values as the message
# Blocklenght is the length of the block on which the DWT Haar transform is 
# performed each time.
# Returns a list of integer stego file samples
def dwtEncryptEncode(coverSamples, message, blockLength, messageType):
      samplesUsed = 0
      
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
          typeMessage = 0
        
      elif (messageType == ".wav"):
          typeMessage = 1
                
      # Insert the type of message as the second element and the message length 
      # as the first element
      message.insert(0, typeMessage)
      message.insert(0, messageLength/1000)
      
      for blockNumber in range(0, len(coefficiets[1])):
          for i in range(0, len(coefficiets[1][blockNumber])):
              # Replace the coefficient by the encrypted ascii char
              
#              if (coefficiets[1][blockNumber][i] > 0):
#                  coefficiets[1][blockNumber][i] = int(coefficiets[1][blockNumber][i]) + message[0]
#                  
#              else:    
#                  coefficiets[1][blockNumber][i] = int(coefficiets[1][blockNumber][i]) - message[0]
              
              coefficiets[1][blockNumber][i] = message[0]
              message = message[1:]
              samplesUsed = blockNumber * blockLength + (i + 1)*2
              

              # If the message is embedded, break
              if (len(message) == 0):
                  doBreak = True
                  break
              
          if (doBreak == True):
              break
              
          
      if (len(message) > 0):
          print("Message bits unembedded:", len(message))
              
      # Reconstruct the signal
      stegoSamples = []
      for i in range(0, len(coefficiets[1])):
          temp = dwt.getSignal(coefficiets[0][i], coefficiets[1][i])
          temp = list(map(float, temp))
          stegoSamples += temp
      
      unaltered = coverSamples[-1*(len(coverSamples) - len(stegoSamples)):]
      print(coefficiets[1][0][0:10])
      return stegoSamples + unaltered, samplesUsed

def dwtEncryptDecode(stegoSamples, blockLength):
      # Get the approximate coefficients and detail coefficients of the signal
      newCoeff = dwt.getCoefficients(stegoSamples, blockLength) 
      print(newCoeff[1][0][0:10])
      extractedLength = 0
      extractMessage = []
      fileType = ''
      blockNumber = 0      
      doBreak = 0
      
      while(1):
          for i in range(0, len(newCoeff[1][blockNumber])):    
              
              extractMessage.append(newCoeff[1][blockNumber][i])
              
              # Interpret the message length and the message type  
              if (len(extractMessage) == 2):
                  #extractedLength = int(school_round((extractMessage[0]-int(extractMessage[0]))*10000, 0))

                  extractedLength = int(school_round(extractMessage[0]*1000, 0))

                  if (extractMessage[1] == 0):
                      fileType = '.txt'

                  elif (extractMessage[1] == 1):
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
          #extractMessage[i] = int(school_round((np.abs(extractMessage[i])-np.abs(int(extractMessage[i]))) * 10000 + count, 0))
          extractMessage[i] = int(school_round(extractMessage[i] * 1000 + count, 0))
      
      # Map the ASCII value to the character version  
      extractMessage = "".join(list(map(chr, extractMessage)))
      
      
      return extractMessage, fileType

