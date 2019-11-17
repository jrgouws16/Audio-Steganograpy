# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 10:05:33 2019

@author: Johan Gouws
"""

import scipy.io.wavfile as scWave
import numpy as np
import AES
import ResultsAndTesting as RT
import dwtFirstPrinciples as dwt
import fileprocessing as fp
from copy import deepcopy
import os



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
      
          samplesUsed = (blockNumber + 1) * 512
      
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
                  
                  subbandCoeff[i][j] = subbandCoeff[i][j] * scalingValue  
                  intValue = int(subbandCoeff[i][j])
                  
                  binaryWidth = 25
                  binaryValue = np.binary_repr(intValue, binaryWidth)
                  binaryValue = list(binaryValue)
                  
                 
                  for k in range(10,25): 
                        
                        if (k - 10 < LSBs):
                              binaryValue[k] = message[0]
                              message = message[1:]
                              
                              if (len(message) == 0):
                                  doBreak = True
                                  break
                        
                        elif(k - 10 == LSBs):
                              binaryValue[k] = '1'
                              
                        else:
                              binaryValue[k] = '0'
                        
                  binaryValue = "".join(binaryValue)          
     
                  if (scalingValue != 0):
                      subbandCoeff[i][j] = (binaryToInt(binaryValue))/scalingValue
     
        
        
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
                  

                  for k in range(10,25): 
                        
                        if (k - 10 < LSBs):
                              
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
                            
                        else:
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

    
      
sigmas = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
errSucc = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
SNR = [0]*9



allPaths = ['C:/Users/Johan Gouws/Desktop/GenresDatabase - Copy/Alternative',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase - Copy/Blues',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase - Copy/Electronic',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase - Copy/Jazz',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase - Copy/Pop',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase - Copy/Rock']

numSongsPerGenre = 100

x = ['Alternative','Blues','Electronic','Jazz','Pop','Rock']
x = np.asarray(x)


for path in allPaths:
      coverFiles = []
                
      for r, d, f in os.walk(path):
            for file in f:
                  if '.wav' in file:
                      coverFiles.append(os.path.join(r, file))
      
      
            coverFiles = coverFiles[0:numSongsPerGenre]

      for t in coverFiles:
            # Receive the message file
            fileType = '.txt'
               
            samplesOne, samplesTwo, rate = fp.getWaveSamples(t)
              
            message = ""
              
            AESkeyEncode = 'AES_KEY'
            
            if (fileType == ".wav"):
                
                  # Get the audio samples in integer form
                  intSamples = fp.extractWaveMessage('Media.ShortOpera.wav')
                  
                  # Convert to integer list of bits for embedding
                  message = "".join(intSamples[0])
                  message = AES.encryptBinaryCTRString(message, AESkeyEncode)      
                  message = list(map(int, list(message)))
                  
            else:
                  message = fp.getMessageBits('Media/text.txt')
                  message = list(map(str, message))
                  message = "".join(message)
                  message = AES.encryptBinaryCTRString(message, AESkeyEncode)
                  message = list(map(int, list(message)))
                  
            
            
            LSBs= 6
                  
            message = "".join(list(map(str, message)))
            originalCoverSamples = deepcopy(samplesOne)
            stegoSamples, samplesUsed, capacityWarning = dwtScaleEncode(samplesOne, message, fileType, LSBs)
            
            
            
            stegoSamples = np.asarray(stegoSamples)
            
            for sigma in range(0,len(sigmas)):
                  
                  mu = 0 # mean and standard deviation
                  noise = np.random.normal(mu, sigmas[sigma], size=len(stegoSamples))
                  noisySamples = []
                                          
                  for i in range(0,len(stegoSamples)):
                        noisySamples.append(stegoSamples[i]+noise[i])
                  noisySamples = np.asarray(noisySamples)
            
            
                  infoMessage = "Capacity: " + str(round(len(message)/samplesUsed, 2)) + " bits per sample."
                  infoMessage += "\nSNR: " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], noisySamples[0:samplesUsed] ), 2))
            
                  noisySNR = round(RT.getSNR(originalCoverSamples[0:samplesUsed], noisySamples[0:samplesUsed] ), 2)
            
                  noisySamples = noisySamples.astype(np.float32, order='C') / 32768.0
                  scWave.write("ROBUSTNESS.wav", rate, noisySamples)
                  
                  AESkeyDecode = "AES_KEY"
                  samplesOneStego, samplesTwoStego, rate = fp.getWaveSamples("ROBUSTNESS.wav")
                  samplesOneStego = np.asarray(samplesOneStego, dtype=np.float32, order = 'C') * 32768.0
                    
                  extractMessage, fileType = dwtScaleDecode(list(samplesOneStego), LSBs)
                  extractMessage = AES.decryptBinaryCTRString(extractMessage, AESkeyDecode)
                    
                  if (AES.bits2string(extractMessage) == "WRONG_KEY"):
                        fileType = '.txt'
                        extractMessage = fp.messageToBinary('Unauthorised access.\n Wrong AES password provided')
                                                        
                  
                  if (fileType == ".wav"):
                        fp.writeWaveMessageToFile(extractMessage, 'ROBUSTNESSmsg.wav')
                    
                  else:
                        fp.writeMessageBitsToFile(extractMessage, 'ROBUSTNESSmsg.txt')
                        
                  
                  compObj1 = open('Media/text.txt', 'r')
                  compObj2 = open('ROBUSTNESSmsg.txt', 'r')
                  
                  if (compObj1.read() != compObj2.read()):
                        errSucc[sigma][0] += 1
                  else:
                        errSucc[sigma][1] += 1
                  
                  print("Sigma =", sigmas[sigma], ", song = " + t[t.index('\\') + 1:],end=" ")
                  print("SNR = ", noisySNR, "[Errors, Success] =",errSucc)

                  SNR[sigma] += noisySNR
                  
print('SNR fpr sigma = 0.1 =', SNR[0]/(numSongsPerGenre*6))
print('SNR fpr sigma = 0.2 =', SNR[1]/(numSongsPerGenre*6))
print('SNR fpr sigma = 0.3 =', SNR[2]/(numSongsPerGenre*6))
print('SNR fpr sigma = 0.4 =', SNR[3]/(numSongsPerGenre*6))
print('SNR fpr sigma = 0.5 =', SNR[4]/(numSongsPerGenre*6))
print('SNR fpr sigma = 0.6 =', SNR[5]/(numSongsPerGenre*6))
print('SNR fpr sigma = 0.7 =', SNR[6]/(numSongsPerGenre*6))
print('SNR fpr sigma = 0.8 =', SNR[7]/(numSongsPerGenre*6))
print('SNR fpr sigma = 0.9 =', SNR[8]/(numSongsPerGenre*6))