# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 12:42:18 2019

@author: project
"""

import pywt
import fileprocessing as fp
import wave
import binascii

def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return int2bytes(n).decode(encoding, errors)

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
    
    for i in range(0,17):
        if (2 ** i > coefficient):
            p = i - 1
            break
        
    return p

# Function to embed a message within a single sample. Will start at 3rd LSB 
def encodeCoefficient(sample, message):
        
    for i in range(3, 3 + len(message)):
        sample = replaceBit(sample, i, message[i - 3])
        
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
    
    for i in range(3, 3 + bits):
        msg += extractBit(sample, i)

    return msg

# Type of wavelet to use
wavletType = pywt.Wavelet('haar')

# Open the cover audio
song = wave.open('Media/opera.wav', mode='rb')

# Extract the wave samples from the host signal
samplesOne, samplesTwo = fp.extractWaveSamples(song)

# Get the approximate coefficients and detail coefficients of the signal
cA_1, cD_1 = pywt.wavedec(samplesOne, wavletType, level=1)

# Write the message that is to be embedded
message = "Goodness gracious"

# Add the length of the message to be encoded as the first 24 bits of the msg

# Convert the message to a binary sequence
message = fp.messageToBinary(message)

messageLength = len(message)
messageLength = '{0:024b}'.format(messageLength)
message = messageLength + message



extractMessage = ''

# Amount of bits to keep of the coefficient
OBH = 12

# Embed the message
for i in range(0, len(cD_1)):
 
    # Calculate the amount of bits that can possibly hidden
    replaceBits = calcPower(cD_1[i]) - OBH
        
    # If it returns as a negative amount, skip the sample
    if (replaceBits <= 0):
        continue
    
    else:
        # Get the amount of message bits that will be embedded
        embedMessage = message[:replaceBits]
        message = message[replaceBits:]
        
        # Replace the message in the coefficient of level 1 detailed coeff
        cD_1[i] = encodeCoefficient(int(cD_1[i]), embedMessage)

        # If the message is embedded, break
        if (len(message) == 0):
            break

# Reconstruct the signal
stegoSamples = pywt.waverec([cA_1, cD_1], wavletType)
stegoSamples = list(map(int, stegoSamples))

# Write to the stego song file
fp.writeStegoToFile('Media/DWT.wav',song.getparams(), stegoSamples)



extractedLength = 0

for i in range(0, len(cD_1)):    
    replaceBits = calcPower(cD_1[i]) - OBH
       
    if (replaceBits <= 0):
        continue
    
    else:
        extractMessage += decodeCoefficient(cD_1[i], replaceBits)
        
        if (len(extractMessage) == 24):
            extractedLength = int(extractMessage, 2)
            
        else:
            if (len(extractMessage) == extractedLength + 24):
                extractMessage = extractMessage[24:]
                break
        
temp = ''
for i in range(int(len(extractMessage)/8)):
    temp += text_from_bits(extractMessage[:8])
    extractMessage = extractMessage[8:]        
        
        
print(temp)





        
        
        
        
        