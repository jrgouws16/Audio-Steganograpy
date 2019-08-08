# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 12:42:18 2019

@author: project
"""

import pywt
import fileprocessing as fp
import wave
import binascii
import numpy as np
import math

def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    if (n > 0 and n < 126):
        return int2bytes(n).decode(encoding, errors)

    else:
        return 'x'
def int2bytes(i):
    hex_string = '%x' % i
    n = len(hex_string)
 
    return binascii.unhexlify(hex_string.zfill(n + (n & 1)))

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

# Function to embed a message within a single sample. Will start at 3rd LSB 
def encodeCoefficient(sample, message):
        
    
    sample = replaceBit(sample, 1, '1')  
    sample = replaceBit(sample, 2, '0')  
    sample = replaceBit(sample, 3, '1')  
    
        
      
    for i in range(4, 4 + len(message)):
        sample = replaceBit(sample, i, message[i - 4])
        
    return sample
    

# Function to extract the ith bit of a sample
def extractBit(sample, LSB_number):
    # Form a sixteen bit sample value string
    sample = "{0:016b}".format(int(sample))
    
    # Return the bit
    return sample[-1*LSB_number]     
    
# Function to embed a message within a single sample. Will start at 3rd LSB 
def decodeCoefficient(sample, bits):
    msg = ''    
    
    for i in range(4, 4 + bits):
        msg += extractBit(sample, i)
        
    return msg

# Fucntion to split song into 2048 bit block samples and returns coefficients
# Takes in integer samples and returns coefficients in form 
# [cA_1[...], cD_1[...]], thus [0][0] will return first list of cA coefficients
#                              [1][5] will return sixth list of cD coefficients    
# Depth is at level one
def getCoefficients(samples, blockLength):
    blocks = int(len(samples) / blockLength)
    
    coefficients = [[],[]]
    wavletType = pywt.Wavelet('haar')


    for i in range(0, math.floor(blocks)):     
        cA_1, cD_1 = pywt.wavedec(samples[i * blockLength: i * blockLength + blockLength], wavletType, level=1)
        coefficients[0].append(cA_1)
        coefficients[1].append(cD_1)
            
    return coefficients
    







# Type of wavelet to use
wavletType = pywt.Wavelet('haar')

# Open the cover audio
song = wave.open('Media/song.wav', mode='rb')

# Extract the wave samples from the host signal
samplesOne, samplesTwo = fp.extractWaveSamples(song)

# Get the approximate coefficients and detail coefficients of the signal
coefficiets = getCoefficients(samplesOne, 2048)

# Message to embed
message = fp.getMessageBits('Media/cat.jpeg')
message = "".join(list(map(str, message)))

messageLength = len(message)

originalMessage = message

messageLength = '{0:024b}'.format(messageLength)
message = messageLength + message


# Amount of bits to keep of the coefficient
OBH = 2
print("############ EMBEDDING   #################")
# Embed the message

blockNumber = 0      
while(len(message) > 0):      
    for i in range(0, len(coefficiets[1][blockNumber])):
        # Calculate the amount of bits that can possibly hidden
        replaceBits = calcPower(coefficiets[1][blockNumber][i]) - OBH - 3
            
        if (len(message) > 1 and blockNumber == len(samplesOne)/2048 -1 and i == len(coefficiets[1][blockNumber]) - 5):
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
            
    
            # If the message is embedded, break
            if (len(message) == 0):
                break
    
    blockNumber+=1


# Reconstruct the signal
stegoSamples = []
for i in range(0, len(coefficiets[1])):
    temp = pywt.waverec([coefficiets[0][i], coefficiets[1][i]], wavletType)
    temp = list(map(int, temp))
    stegoSamples += temp



for i in range(len(stegoSamples)):
      if (stegoSamples[i] > 32767):
            stegoSamples[i] = 32767
      
      if (stegoSamples[i] < -32767):
            stegoSamples[i] = -32767
      
print("############ WRITING   #################")

# Write to the stego song file
fp.writeStegoToFile('Media/DWT.wav',song.getparams(), stegoSamples)


print("############ EXTRACTING   #################")
####################   From stego file   ######################################
extractMessage = ''
# Open the cover audio
stego = wave.open('Media/DWT.wav', mode='rb')

# Extract the wave samples from the host signal
samplesOneStego, samplesTwoStego = fp.extractWaveSamples(stego)

# Get the approximate coefficients and detail coefficients of the signal
newCoeff = getCoefficients(samplesOneStego, 2048)
    
extractedLength = 0
foundMsgLength = False

extractMessage = ''

blockNumber = 0      
doBreak = 0

while(1):
    for i in range(0, len(coefficiets[1][blockNumber])):    
        
        replaceBits = calcPower(coefficiets[1][blockNumber][i]) - OBH - 3
           
        if (replaceBits <= 0):
            continue
        
        else:
            extractMessage += decodeCoefficient(coefficiets[1][blockNumber][i], replaceBits)
    
            if (len(extractMessage) >= 24 and foundMsgLength == False):
                extractedLength = int(extractMessage[0:24], 2)
                foundMsgLength = True
                
            else:
                if (len(extractMessage) >= extractedLength + 24 and foundMsgLength == True):
                    extractMessage = extractMessage[24:24 + extractedLength]
                    
                    doBreak = 1
                    break
             
    blockNumber += 1
    if(doBreak == 1):
        break
    
fp.writeMessageBitsToFile(extractMessage, 'Media/ck.jpeg')
