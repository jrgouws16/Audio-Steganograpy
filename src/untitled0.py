import ResultsAndTesting as RT
import dwtHybrid
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

numSongsPerGenre = 1
textMessage = True

x = ['Alternative','Blues','Electronic','Jazz','Pop','Rock']
x = np.asarray(x)

OBHs = [7,11]


for OBH_index in range(0,len(OBHs)):
      AESkeyEncode = "THIS_IS_THE_KEY_USED_FOR_AES_ENCRYPTION"
  
      samplesOne, samplesTwo, rate = fp.getWaveSamples('C:/Users/Johan Gouws/Desktop/GenresDatabase/Blues\All_Men_Are_Dogs_-GIGOLETTE.wav')
#      samplesOne, samplesTwo, rate = fp.getWaveSamples('C:/Users/Johan Gouws/Desktop/GenresDatabase/Alternative\Happy_Medium-Misty_blue.wav')
      message = ""
      message = fp.getMessageBits('C:/Users/Johan Gouws/Desktop/Audio-Steganograpy/src/Media/text.txt')
      message = list(map(str, message))
      message = "".join(message)
      originalMessage = deepcopy(message)
      message = AES.encryptBinaryString(message, AESkeyEncode)
      message = list(map(int, list(message)))
      message = "".join(list(map(str, message)))
      
    
      currentTime = time.time()
#      stegoSamples, samplesUsed, capacityWarning,encP,encC = dwtHybrid.dwtHybridEncode(samplesOne, message, '.txt', OBHs[OBH_index])
      stegoSamples, samplesUsed, capacityWarning = dwtHybrid.dwtHybridEncode(samplesOne, message, '.txt', OBHs[OBH_index])

      if (capacityWarning == True):
            print("Whoah the capacity is too small of the cover file")

      stegoSamples = np.asarray(stegoSamples, dtype=np.float32, order = 'C')/32768.0
      scWave.write("Stego5.wav", rate, stegoSamples)
  
      # Open the steganography file
      samplesOneStego, samplesTwoStego, rate = fp.getWaveSamples("Stego5.wav")
      samplesOneStego = np.asarray(samplesOneStego, dtype=np.float32, order = 'C')*32768.0
        
      # Extract the wave samples from the host signal
      currentTime = time.time()
#      extractMessage, fileType,decP,decC = dwtHybrid.dwtHybridDecode(samplesOneStego, OBHs[OBH_index])
      extractMessage, fileType = dwtHybrid.dwtHybridDecode(samplesOneStego, OBHs[OBH_index])


      extractMessage = AES.decryptBinaryString(extractMessage, "THIS_IS_THE_KEY_USED_FOR_AES_ENCRYPTION")

      if (originalMessage != extractMessage):
            print("ERROR")
            
      else:
            print("SUCCESS")
            
            
#      for i in range(0, len(decP)):      
#            if (encP[i]!=decP[i]):
#                  print(encP[i],decP[i],encC[i],decC[i])
                  
