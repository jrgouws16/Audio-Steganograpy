import ResultsAndTesting as RT
import dwtEncrypt
import fileprocessing as fp
import numpy as np
import matplotlib.pyplot as plt

import scipy.io.wavfile as scWave
from copy import deepcopy
import time
import os
import AES


allPaths = ['C:/Users/Johan Gouws/Desktop/GenresDatabase/Alternative',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Blues',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Electronic',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Jazz',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Pop',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Rock']

numSongsPerGenre = 50
textMessage = True

SNRAlt = 0
SNRBlu = 0
SNREle = 0
SNRJzz = 0
SNRPop = 0
SNRRoc = 0

CapAlt = 0
CapBlu = 0
CapEle = 0
CapJzz = 0
CapPop = 0
CapRoc = 0

SamAlt = 0
SamBlu = 0
SamEle = 0
SamJzz = 0
SamPop = 0
SamRoc = 0

counter = numSongsPerGenre * 6

for path in allPaths:
      coverFiles = []
          
      for r, d, f in os.walk(path):
        for file in f:
            if '.wav' in file:
                coverFiles.append(os.path.join(r, file))


      coverFiles = coverFiles[0:numSongsPerGenre]
      if (textMessage == True):
            
            for t in coverFiles:
                  samplesOne, samplesTwo, rate = fp.getWaveSamples(t)
                                      
                  message = ""
                  messageObject = open('C:/Users/Johan Gouws/Desktop/Audio-Steganograpy/src/Media/text.txt', "r")
                      
                  # Extract the message as a string of characters
                  message = messageObject.read()
                  messageObject.close()
                                          
                  originalCoverSamples = deepcopy(samplesOne)
                  stegoSamples, samplesUsed, capacityWarning = dwtEncrypt.dwtEncryptEncode(samplesOne, message, 2048, '.txt')        
                                      
                  SNR = RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] )
                  capacity = RT.getCapacity(message*8, samplesUsed, rate)
                  
                  print(counter, end=" ")
                  counter -= 1                  
                  
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Alternative'):
                       SNRAlt += SNR
                       CapAlt += capacity
                       SamAlt += samplesUsed
                       
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Blues'):
                       SNRBlu += SNR
                       CapBlu += capacity
                       SamBlu += samplesUsed
                       
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Electronic'):
                       SNREle += SNR
                       CapEle += capacity
                       SamEle += samplesUsed
                       
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Jazz'):
                       SNRJzz += SNR
                       CapJzz += capacity
                       SamJzz += samplesUsed
                       
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Pop'):
                       SNRPop += SNR
                       CapPop += capacity
                       SamPop += samplesUsed
                       
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Rock'):
                       SNRRoc += SNR
                       CapRoc += capacity
                       SamRoc += samplesUsed
                       
x = ['Alternative','Blues','Electronic','Jazz','Pop','Rock']
x = np.asarray(x)       
              
plt.figure(7)
plt.ylabel('SNR (dB)')
plt.plot(x, [SNRAlt/numSongsPerGenre,SNRBlu/numSongsPerGenre,SNREle/numSongsPerGenre,SNRJzz/numSongsPerGenre,SNRPop/numSongsPerGenre,SNRRoc/numSongsPerGenre])
plt.figure(8)
plt.ylabel('Capacity (bits per 16 bit cover sample)')
plt.plot(x, [CapAlt*1000/44100/numSongsPerGenre,CapBlu*1000/44100/numSongsPerGenre,CapEle*1000/44100/numSongsPerGenre,CapJzz*1000/44100/numSongsPerGenre,CapPop*1000/44100/numSongsPerGenre,CapRoc*1000/44100/numSongsPerGenre])
plt.figure(9)
plt.ylabel('Samples Used')
plt.plot(x, [SamAlt/numSongsPerGenre,SamBlu/numSongsPerGenre,SamEle/numSongsPerGenre,SamJzz/numSongsPerGenre,SamPop/numSongsPerGenre,SamRoc/numSongsPerGenre])
            

