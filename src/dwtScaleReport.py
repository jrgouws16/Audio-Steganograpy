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

numSongsPerGenre = 1
textMessage = True

x = ['Alternative','Blues','Electronic','Jazz','Pop','Rock']
x = np.asarray(x)

SNRAlt = [0,0,0,0,0,0,0,0,0,0,0]
SNRBlu = [0,0,0,0,0,0,0,0,0,0,0]
SNREle = [0,0,0,0,0,0,0,0,0,0,0]
SNRJzz = [0,0,0,0,0,0,0,0,0,0,0]
SNRPop = [0,0,0,0,0,0,0,0,0,0,0]
SNRRoc = [0,0,0,0,0,0,0,0,0,0,0]

CapAlt = [0,0,0,0,0,0,0,0,0,0,0]
CapBlu = [0,0,0,0,0,0,0,0,0,0,0]
CapEle = [0,0,0,0,0,0,0,0,0,0,0]
CapJzz = [0,0,0,0,0,0,0,0,0,0,0]
CapPop = [0,0,0,0,0,0,0,0,0,0,0]
CapRoc = [0,0,0,0,0,0,0,0,0,0,0]

SamAlt = [0,0,0,0,0,0,0,0,0,0,0]
SamBlu = [0,0,0,0,0,0,0,0,0,0,0]
SamEle = [0,0,0,0,0,0,0,0,0,0,0]
SamJzz = [0,0,0,0,0,0,0,0,0,0,0]
SamPop = [0,0,0,0,0,0,0,0,0,0,0]
SamRoc = [0,0,0,0,0,0,0,0,0,0,0]

counter = numSongsPerGenre * 6 * 11
capacityWarnings = 0
LSBs = [1,2,3,4,5,6,7,8,9,10,11]

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
                             SNRAlt[LSB-1] += SNR
                             CapAlt[LSB-1] += capacity
                             SamAlt[LSB-1] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Blues'):
                             SNRBlu[LSB-1] += SNR
                             CapBlu[LSB-1] += capacity
                             SamBlu[LSB-1] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Electronic'):
                             SNREle[LSB-1] += SNR
                             CapEle[LSB-1] += capacity
                             SamEle[LSB-1] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Jazz'):
                             SNRJzz[LSB-1] += SNR
                             CapJzz[LSB-1] += capacity
                             SamJzz[LSB-1] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Pop'):
                             SNRPop[LSB-1] += SNR
                             CapPop[LSB-1] += capacity
                             SamPop[LSB-1] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Rock'):
                             SNRRoc[LSB-1] += SNR
                             CapRoc[LSB-1] += capacity
                             SamRoc[LSB-1] += samplesUsed
                       
                       
                  print("capacityWarnings = ", capacityWarnings)
                  capacityWarning = 0


for LSB in LSBs:
      plt.figure(4)
      plt.title('SNR')
      plt.plot(x, [SNRAlt[LSB-1]/numSongsPerGenre,SNRBlu[LSB-1]/numSongsPerGenre,SNREle[LSB-1]/numSongsPerGenre,SNRJzz[LSB-1]/numSongsPerGenre,SNRPop[LSB-1]/numSongsPerGenre,SNRRoc[LSB-1]/numSongsPerGenre])
      plt.figure(5)
      plt.title('Capacity')
      plt.plot(x, [CapAlt[LSB-1]*1000/44100/numSongsPerGenre,CapBlu[LSB-1]*1000/44100/numSongsPerGenre,CapEle[LSB-1]*1000/44100/numSongsPerGenre,CapJzz[LSB-1]*1000/44100/numSongsPerGenre,CapPop[LSB-1]*1000/44100/numSongsPerGenre,CapRoc[LSB-1]*1000/44100/numSongsPerGenre])
      plt.figure(6)
      plt.title('Samples Used')
      plt.plot(x, [SamAlt[LSB-1]/numSongsPerGenre,SamBlu[LSB-1]/numSongsPerGenre,SamEle[LSB-1]/numSongsPerGenre,SamJzz[LSB-1]/numSongsPerGenre,SamPop[LSB-1]/numSongsPerGenre,SamRoc[LSB-1]/numSongsPerGenre])