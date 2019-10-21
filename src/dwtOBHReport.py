import ResultsAndTesting as RT
import dwtOBH
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

SNRAlt = [0,0,0,0,0,0,0,0]
SNRBlu = [0,0,0,0,0,0,0,0]
SNREle = [0,0,0,0,0,0,0,0]
SNRJzz = [0,0,0,0,0,0,0,0]
SNRPop = [0,0,0,0,0,0,0,0]
SNRRoc = [0,0,0,0,0,0,0,0]

CapAlt = [0,0,0,0,0,0,0,0]
CapBlu = [0,0,0,0,0,0,0,0]
CapEle = [0,0,0,0,0,0,0,0]
CapJzz = [0,0,0,0,0,0,0,0]
CapPop = [0,0,0,0,0,0,0,0]
CapRoc = [0,0,0,0,0,0,0,0]

SamAlt = [0,0,0,0,0,0,0,0]
SamBlu = [0,0,0,0,0,0,0,0]
SamEle = [0,0,0,0,0,0,0,0]
SamJzz = [0,0,0,0,0,0,0,0]
SamPop = [0,0,0,0,0,0,0,0]
SamRoc = [0,0,0,0,0,0,0,0]

counter = numSongsPerGenre * 6 * 8
capacityWarnings = 0
OBHs = [0,1,2,3,4,5,6,7]

for path in allPaths:
      coverFiles = []
          
      for r, d, f in os.walk(path):
        for file in f:
            if '.wav' in file:
                coverFiles.append(os.path.join(r, file))


      coverFiles = coverFiles[0:numSongsPerGenre]
      if (textMessage == True):
            
            for t in coverFiles:
                  for OBH in OBHs:
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
                                          
                        stegoSamples, samplesUsed, capacityWarning = dwtOBH.dwtHaarEncode(samplesOne, message, OBH, 2048, '.txt')
                                            
                        if (capacityWarning == True):
                              capacityWarnings += 1
                        
                        # Get the characteristics of the stego file
                        SNR = RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] )
                        capacity = RT.getCapacity(message, samplesUsed, rate)
                        
                        print(counter, end=" ")
                        counter -= 1      
                        
                        
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Alternative'):
                             SNRAlt[OBH] += SNR
                             CapAlt[OBH] += capacity
                             SamAlt[OBH] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Blues'):
                             SNRBlu[OBH] += SNR
                             CapBlu[OBH] += capacity
                             SamBlu[OBH] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Electronic'):
                             SNREle[OBH] += SNR
                             CapEle[OBH] += capacity
                             SamEle[OBH] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Jazz'):
                             SNRJzz[OBH] += SNR
                             CapJzz[OBH] += capacity
                             SamJzz[OBH] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Pop'):
                             SNRPop[OBH] += SNR
                             CapPop[OBH] += capacity
                             SamPop[OBH] += samplesUsed
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Rock'):
                             SNRRoc[OBH] += SNR
                             CapRoc[OBH] += capacity
                             SamRoc[OBH] += samplesUsed
                       
                        
                  print("capacityWarnings = ", capacityWarnings)
                  capacityWarning = 0
                  


for OBH in OBHs:
      plt.figure(1)
      plt.title('SNR')
      plt.plot(x, [SNRAlt[OBH]/numSongsPerGenre,SNRBlu[OBH]/numSongsPerGenre,SNREle[OBH]/numSongsPerGenre,SNRJzz[OBH]/numSongsPerGenre,SNRPop[OBH]/numSongsPerGenre,SNRRoc[OBH]/numSongsPerGenre])
      plt.figure(2)
      plt.title('Capacity')
      plt.plot(x, [CapAlt[OBH]*1000/44100/numSongsPerGenre,CapBlu[OBH]*1000/44100/numSongsPerGenre,CapEle[OBH]*1000/44100/numSongsPerGenre,CapJzz[OBH]*1000/44100/numSongsPerGenre,CapPop[OBH]*1000/44100/numSongsPerGenre,CapRoc[OBH]*1000/44100/numSongsPerGenre])
      plt.figure(3)
      plt.title('Samples Used')
      plt.plot(x, [SamAlt[OBH]/numSongsPerGenre,SamBlu[OBH]/numSongsPerGenre,SamEle[OBH]/numSongsPerGenre,SamJzz[OBH]/numSongsPerGenre,SamPop[OBH]/numSongsPerGenre,SamRoc[OBH]/numSongsPerGenre])