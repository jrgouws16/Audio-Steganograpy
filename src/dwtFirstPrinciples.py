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

# Convolve signal x with signal y
def convolve(x, y):
    lenX = len(x)
    lenY = len(y)
    
    reversedY = np.asarray(y[::-1])
    x = np.asarray(x)
    
    convolved = []
    
    # Before the shifting signal moved over the stationary signal
    for i in range(0, lenY - 1):
        convolved.append(sum(reversedY[-i-1:] * x[:i + 1]))
    
    # While the shifting signal moves over the stationary signal
    for i in range(0, lenX - lenY + 1):
        convolved.append(sum(reversedY * x[i:i + lenY]))
        
    # While the shifting signal is moving over the stationary signal    
    for i in range(0, lenY - 1):
        convolved.append(sum(reversedY[:-i-1] * x[lenX - lenY + i + 1:]))
        
    return convolved

# Takes as input the signal and returns the approximation coefficients
# and detailed coefficients
def getCoeff(signal):
    # Haar coefficients for low pass filter decomposition
    coefLowDec  = [0.7071067811865476,  0.7071067811865476]
    
    # Haar coefficients for high pass filter decomposition
    coefHighDec = [-0.7071067811865476, 0.7071067811865476]

    # Convolve the signal with the low-pass for the approximation coefficients
    approx = convolve(signal, coefLowDec)
    approx = approx[1::2]

    # Convolve the signal with the high-pass for the detailed coefficients
    detail = convolve(signal, coefHighDec)
    detail = detail[1::2]
    return approx, detail

# One level reconstruction of signal from coefficients
def getSignal(approx, detail):
    # Haar coefficients for low pass filter reconstruction
    coefLowRec  = [0.7071067811865476,  0.7071067811865476]
    
    # Haar coefficients for high pass filter reconstruction
    coefHighRec = [0.7071067811865476, -0.7071067811865476]
    
    # Insert zero's every second index, for upsampling, starting at index 0
    for b in range (0,len(approx)):
        approx.insert(b*2,0)

    for b in range (0,len(detail)):
        detail.insert(b*2,0)

    # First index should not be a zero
    del detail[0]
    del approx[0]
 
    # Convolve the coefficients with the filter coefficients
    approxSignal = convolve(approx, coefLowRec)
    detailSignal = convolve(detail, coefHighRec)
    
    # If they are of different lengths, make them of equal lengths
    while (len(approxSignal) < len(detailSignal)):
        approxSignal.append(0)
        
    while (len(approxSignal) > len(detailSignal)):
        detailSignal.append(0)
    
    approxSignal = np.asarray(approxSignal)
    detailSignal = np.asarray(detailSignal)
    
    # Add the results and return the result
    returnList   = list(map(int, list(approxSignal + detailSignal)))
    
    return returnList
    
# Function able to perform Haar DWT of level greater than one
def getLevelCoefficients(levels, signal):
    approx = signal
    detail = []

    for i in range(0, levels):
        approx, det = getCoeff(approx)
        detail.insert(0, det)
    return approx, detail

# Function able to perform Haar IDWT of level greater than one
# Takes approximation coefficients list as first parameter and list of 
# detailed coefficients lists as the second paramenter
def getLevelSignal(approx, detail):
    signal = approx
    
    for i in range(len(detail)):
        signal = getSignal(signal, detail[i])
       
    return signal
       
def getCoefficients(samples, blockLength):
    blocks = int(len(samples) / blockLength)
    
    coefficients = [[],[]]

    for i in range(0, math.floor(blocks)):     
        cA_1, cD_1 = getCoeff(samples[i * blockLength: i * blockLength + blockLength])
        coefficients[0].append(cA_1)
        coefficients[1].append(cD_1)
            
    return coefficients


# Function calculating the p value required to determine 
# number of bits to embed
def calcPower(coefficient):
    p = 0
    
    coefficient = np.abs(coefficient)
    
    for i in range(0,17):
        if (2 ** i > coefficient):
            p = i - 1
            break
        
    if (p == -1):
        p = 0
        
    return p

# Function to place a single bit within a 16 bit cover sample
def replaceBit(sample, LSB_number, bit):
    # Convert the sample to a sixteen bit binary string
    sample = "{0:016b}".format(sample)      
    
    # Convert binary string to a list
    sample = list(sample)                   
    
    # Replace the ith LSB with the bit
    sample[-1*LSB_number] = str(bit)        
    
    # Convert the list to a string
    sample = ''.join(sample)      

    # Return the decimal value  
    return int(sample,2) 

# Function to extract the ith bit of a sample
def extractBit(sample, LSB_number):
    # Form a sixteen bit sample value string
    sample = "{0:016b}".format(int(sample))
    
    # Return the bit
    return sample[-1*LSB_number]  

# Function to embed a message within a single sample. Will start at 3rd LSB 
def encodeCoefficient(sample, message):

    sample = replaceBit(sample, 1, '1')  
    sample = replaceBit(sample, 2, '0')  
    sample = replaceBit(sample, 3, '1')  
    
    for i in range(4, 4 + len(message)):
        sample = replaceBit(sample, i, message[i - 4])
        
    return sample

# Function to embed a message within a single sample. Will start at 3rd LSB 
def decodeCoefficient(sample, bits):
    msg = ''    
    
    for i in range(4, 4 + bits):
        msg += extractBit(sample, i)
        
    return msg

# Function to encode a message within a audio file using the Haar DWT transform
# Takes in list of integer cover file samples
# Takes a binary bit string of the message
# OBH is the number of cover coefficient bits to keep
# Blocklenght is the length of the block on which the DWT Haar transform is 
# performed each time.
# Returns a list of integer stego file samples
def dwtHaarEncode(coverSamples, message, OBH, blockLength, messageType):
      samplesUsed = 0
      
      # Get the approximate coefficients and detail coefficients of the signal
      coefficiets = getCoefficients(coverSamples, blockLength)
      
      # Embed the messagelength within the message
      messageLength = len(message)
      messageLength = '{0:026b}'.format(messageLength)
      
      typeMessage = '{0:02b}'.format(0)
    
      if (messageType == ".txt"):
          typeMessage = '{0:02b}'.format(0)
        
      elif (messageType == ".wav"):
          typeMessage = '{0:02b}'.format(1)
                
      message = messageLength + typeMessage + message
      
      blockNumber = 0      
      while(len(message) > 0):      
          for i in range(0, len(coefficiets[1][blockNumber])):
              # Calculate the amount of bits that can possibly hidden
              replaceBits = calcPower(coefficiets[1][blockNumber][i]) - OBH - 3
                  
              if (len(message) > 1 and blockNumber == len(coverSamples)/blockLength -1 and i == len(coefficiets[1][blockNumber]) - 5):
                    print("Message is too long")
                    print("Unembedded message bits =", len(message))
                    break
          
              # If it returns as a negative amount, skip the sample
              if (replaceBits <= 0):
                  continue
              
              else:
                  # Get the amount of message bits that will be embedded
                  embedMessage = message[:replaceBits]
                  message = message[replaceBits:]
                  coefficiets[1][blockNumber][i] = encodeCoefficient(int(coefficiets[1][blockNumber][i]), embedMessage)
                  samplesUsed = blockNumber * blockLength + (i + 1)*2

                  # If the message is embedded, break
                  if (len(message) == 0):
                      break
          
          blockNumber+=1
      
      
      # Reconstruct the signal
      stegoSamples = []
      for i in range(0, len(coefficiets[1])):
          temp = getSignal(coefficiets[0][i], coefficiets[1][i])
          temp = list(map(int, temp))
          stegoSamples += temp
      
      for i in range(len(stegoSamples)):
            if (stegoSamples[i] > 32767):
                  stegoSamples[i] = 32767
            
            if (stegoSamples[i] < -32767):
                  stegoSamples[i] = -32767

      
      return stegoSamples, samplesUsed
      
# Function to decode a message from a stego audio file using the Haar DWT transform
# Takes in list of integer stego file samples
# OBH is the number of cover coefficient bits to keep
# Blocklenght is the length of the block on which the DWT Haar transform is 
# performed each time.
# Returns a binary bit stream of the message that was extracted
def dwtHaarDecode(stegoSamples, OBH, blockLength):      
      
      # Get the approximate coefficients and detail coefficients of the signal
      newCoeff = getCoefficients(stegoSamples, blockLength)
          
      extractedLength = 0
      foundMsgLength = False
      
      extractMessage = ''
      fileType = ''
      blockNumber = 0      
      doBreak = 0
      
      while(1):
          for i in range(0, len(newCoeff[1][blockNumber])):    
              
              replaceBits = calcPower(newCoeff[1][blockNumber][i]) - OBH - 3
                 
              if (replaceBits <= 0):
                  continue
              
              else:
                  extractMessage += decodeCoefficient(newCoeff[1][blockNumber][i], replaceBits)
          
                  if (len(extractMessage) >= 28 and foundMsgLength == False):
                      extractedLength = int(extractMessage[0:26], 2)
                      foundMsgLength = True
                      
                      if (extractMessage[26:28] == '00'):
                          fileType = '.txt'
    
                      elif (extractMessage[26:28] == '01'):
                          fileType = '.wav'
                      
                  else:
                      if (len(extractMessage) >= extractedLength + 28 and foundMsgLength == True):
                          extractMessage = extractMessage[28:28 + extractedLength]
                          
                          doBreak = 1
                          break
                   
          blockNumber += 1
          if(doBreak == 1):
              break
        
      return extractMessage, fileType
      
      





