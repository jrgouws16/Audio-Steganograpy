import ResultsAndTesting as RT
import dwtScale
import fileprocessing as fp
import numpy as np
import matplotlib.pyplot as plt

import scipy.io.wavfile as scWave
from copy import deepcopy
import time
import os
import AES

textMessage = True

allPaths = ['C:/Users/Johan Gouws/Desktop/GenresDatabase/Alternative',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Blues',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Electronic',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Jazz',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Pop',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Rock']

numSongsPerGenre = 50
textMessage = True

x = ['Alternative','Blues','Electronic','Jazz','Pop','Rock']
x = np.asarray(x)

SNRAlt = [0,0,0,0,0,0,0]
SNRBlu = [0,0,0,0,0,0,0]
SNREle = [0,0,0,0,0,0,0]
SNRJzz = [0,0,0,0,0,0,0]
SNRPop = [0,0,0,0,0,0,0]
SNRRoc = [0,0,0,0,0,0,0]

CapAlt = [0,0,0,0,0,0,0]
CapBlu = [0,0,0,0,0,0,0]
CapEle = [0,0,0,0,0,0,0]
CapJzz = [0,0,0,0,0,0,0]
CapPop = [0,0,0,0,0,0,0]
CapRoc = [0,0,0,0,0,0,0]

SamAlt = [0,0,0,0,0,0,0]
SamBlu = [0,0,0,0,0,0,0]
SamEle = [0,0,0,0,0,0,0]
SamJzz = [0,0,0,0,0,0,0]
SamPop = [0,0,0,0,0,0,0]
SamRoc = [0,0,0,0,0,0,0]

counter = numSongsPerGenre * 6 * 7
capacityWarnings = 0
LSBs = [1,2,3,4,5,6]

for path in allPaths:
      coverFiles = []
          
      for r, d, f in os.walk(path):
        for file in f:
            if '.wav' in file:
                coverFiles.append(os.path.join(r, file))


      coverFiles = coverFiles[0:numSongsPerGenre]
      if (textMessage == True):
            
            for t in coverFiles:
                  for LSB in LSBs:

                        AESkeyEncode = "THIS_IS_THE_KEY_USED_FOR_AES_ENCRYPTION"
                        
                        samplesOne, samplesTwo, rate = fp.getWaveSamples(t)
                                            
                        message = ""
                        message = fp.getMessageBits('C:/Users/Johan Gouws/Desktop/Audio-Steganograpy/src/Media/text.txt')
                        message = list(map(str, message))
                        message = "".join(message)
                        message = AES.encryptBinaryString(message, AESkeyEncode)
                        message = list(map(int, list(message)))
                        message = "".join(list(map(str, message)))
                        originalCoverSamples = deepcopy(samplesOne)
                        
                        stegoSamples, samplesUsed, capacityWarning = dwtScale.dwtScaleEncode(samplesOne, message, '.txt', LSB)
                        
                        
                        if (capacityWarning == True):
                              capacityWarnings += 1
                                                
                        # Get the characteristics of the stego file
                        SNR = RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] )
                        capacity = RT.getCapacity(message, samplesUsed, rate)
                              
                        print(counter, end=" ")
                        counter -= 1      
                        
                        
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Alternative'):
                             SNRAlt[LSB] += SNR
                             CapAlt[LSB] += capacity
                             SamAlt[LSB] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Blues'):
                             SNRBlu[LSB] += SNR
                             CapBlu[LSB] += capacity
                             SamBlu[LSB] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Electronic'):
                             SNREle[LSB] += SNR
                             CapEle[LSB] += capacity
                             SamEle[LSB] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Jazz'):
                             SNRJzz[LSB] += SNR
                             CapJzz[LSB] += capacity
                             SamJzz[LSB] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Pop'):
                             SNRPop[LSB] += SNR
                             CapPop[LSB] += capacity
                             SamPop[LSB] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Rock'):
                             SNRRoc[LSB] += SNR
                             CapRoc[LSB] += capacity
                             SamRoc[LSB] += samplesUsed
                       
                       
                  print("capacityWarnings = ", capacityWarnings)
                  capacityWarning = 0


for LSB in LSBs:
      plt.figure(4)
      plt.title('SNR')
      plt.plot(x, [SNRAlt[LSB]/numSongsPerGenre,SNRBlu[LSB]/numSongsPerGenre,SNREle[LSB]/numSongsPerGenre,SNRJzz[LSB]/numSongsPerGenre,SNRPop[LSB]/numSongsPerGenre,SNRRoc[LSB]/numSongsPerGenre])
      plt.figure(5)
      plt.title('Capacity')
      plt.plot(x, [CapAlt[LSB]*1000/44100/numSongsPerGenre,CapBlu[LSB]*1000/44100/numSongsPerGenre,CapEle[LSB]*1000/44100/numSongsPerGenre,CapJzz[LSB]*1000/44100/numSongsPerGenre,CapPop[LSB]*1000/44100/numSongsPerGenre,CapRoc[LSB]*1000/44100/numSongsPerGenre])
      plt.figure(6)
      plt.title('Samples Used')
      plt.plot(x, [SamAlt[LSB]/numSongsPerGenre,SamBlu[LSB]/numSongsPerGenre,SamEle[LSB]/numSongsPerGenre,SamJzz[LSB]/numSongsPerGenre,SamPop[LSB]/numSongsPerGenre,SamRoc[LSB]/numSongsPerGenre])