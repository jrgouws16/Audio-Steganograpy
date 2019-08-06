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

# Type of wavelet to use
wavletType = pywt.Wavelet('haar')

# Open the cover audio
song = wave.open('Media/opera.wav', mode='rb')

# Extract the wave samples from the host signal
samplesOne, samplesTwo = fp.extractWaveSamples(song)

# Get the approximate coefficients and detail coefficients of the signal
cA_1, cD_1 = pywt.wavedec(samplesOne, wavletType, level=1)

# Write the message that is to be embedded
message = fp.getMessageBits('Media/text.txt')
message = "".join(list(map(str, message)))

message = 'First DWT Text steganography encoded and extracted successufully\n'*400


# Convert the message to a binary sequence
message = fp.messageToBinary(message)

messageLength = len(message)
messageLength = '{0:024b}'.format(messageLength)
message = messageLength + message

print(len(message), "Message bits encoded within", len(samplesOne), "samples")
print(len(message)/8, "bits/second encoding")
print("Capacity (%) =",len(message)/(len(samplesOne)*16)*100)

extractMessage = ''

# Amount of bits to keep of the coefficient
OBH = 6

print("############ EMBEDDING   #################")
# Embed the message
for i in range(0, len(cD_1)):
    # Calculate the amount of bits that can possibly hidden
    replaceBits = calcPower(cD_1[i]) - OBH
   
    if (len(message) > 1 and i == len(cD_1) - 1):
          print("Message is too long")
          break
    
    
    # If it returns as a negative amount, skip the sample
    if (replaceBits <= 0):
        continue
    
    else:
        # Get the amount of message bits that will be embedded
        embedMessage = message[:replaceBits]
        message = message[replaceBits:]
        cD_1[i] = encodeCoefficient(int(cD_1[i]), embedMessage)
        

        # If the message is embedded, break
        if (len(message) == 0):
            break

# Reconstruct the signal
stegoSamples = pywt.waverec([cA_1, cD_1], wavletType)
stegoSamples = list(map(int, stegoSamples))

for i in range(len(stegoSamples)):
      if (stegoSamples[i] > 32767):
            stegoSamples[i] = 32767
      
      if (stegoSamples[i] < -32767):
            stegoSamples[i] = -32767
      
print("############ WRITING   #################")

# Write to the stego song file
fp.writeStegoToFile('Media/DWT.wav',song.getparams(), stegoSamples)

print("############ Reading   #################")


print("############ EXTRACTING 1   #################")
####################   From stego file   ######################################

# Open the cover audio
stego = wave.open('Media/DWT.wav', mode='rb')

# Extract the wave samples from the host signal
samplesOneStego, samplesTwoStego = fp.extractWaveSamples(stego)

# Get the approximate coefficients and detail coefficients of the signal
cA_1_new, cD_1_new = pywt.wavedec(samplesOneStego, wavletType, level=1)
    
extractedLength = 0
foundMsgLength = False

extractMessage = ''

for i in range(0, len(cD_1_new)):    
    replaceBits = calcPower(cD_1_new[i]) - OBH
       
    if (replaceBits <= 0):
        continue
    
    else:
        extractMessage += decodeCoefficient(cD_1_new[i], replaceBits)

        if (len(extractMessage) >= 24 and foundMsgLength == False):
            extractedLength = int(extractMessage[0:24], 2)
            foundMsgLength = True
            
        else:
            if (len(extractMessage) >= extractedLength + 24 and foundMsgLength == True):
                extractMessage = extractMessage[24:]
                break
        
temp = ''

while(len(extractMessage) >= 8):
    temp += text_from_bits(extractMessage[:8])
    extractMessage = extractMessage[8:]        
        
        
print(temp)

print("############ EXTRACTING 2   #################")
#####################   From current  #########################################
'''
extractedLength = 0
foundMsgLength = False

extractMessage = ''

for i in range(0, len(cD_1)):    
    replaceBits = calcPower(cD_1[i]) - OBH
       
    if (replaceBits <= 0):
        continue
    
    else:
        extractMessage += decodeCoefficient(cD_1[i], replaceBits)

        if (len(extractMessage) >= 24 and foundMsgLength == False):
            extractedLength = int(extractMessage[0:24], 2)
            foundMsgLength = True
            
        else:
            if (len(extractMessage) >= extractedLength + 24 and foundMsgLength == True):
                extractMessage = extractMessage[24:]
                break
        
temp = ''

while(len(extractMessage) >= 8):
    temp += text_from_bits(extractMessage[:8])
    extractMessage = extractMessage[8:]        
    
#print(temp)


'''
        
        












































        
        