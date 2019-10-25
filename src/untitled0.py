#import numpy as np
#
#
#noise = np.random.normal(0, 0.5, 100000)
#
#
#belowSNR  = []
#
#for i in range(5):
#      belowSNR.append([0]*4)

import dwtHybrid
import fileprocessing as fp
import numpy as np

import scipy.io.wavfile as scWave
from copy import deepcopy
import AES

rate, samples = scWave.read('C:/Users/Johan Gouws/Desktop/Audio-Steganograpy/src/Media/ShortOpera.wav')
scWave.write('C:/Users/Johan Gouws/Desktop/Audio-Steganograpy/src/Media/ShortOperaNew.wav',rate,samples[0:4071])
rate, samples = scWave.read('C:/Users/Johan Gouws/Desktop/GenresDatabase/Alternative/Anders_Tengdahl-I_came_here_to_see_you.wav')

message = ""
message = fp.getMessageBits('C:/Users/Johan Gouws/Desktop/Audio-Steganograpy/src/Media/text.txt')
message = list(map(str, message))
message = "".join(message)

print(len(message))
print(message[0:10])
# Get the audio samples in integer form
intSamples = fp.extractWaveMessage('C:/Users/Johan Gouws/Desktop/Audio-Steganograpy/src/Media/ShortOperaNew.wav')
    
# Convert to integer list of bits for embedding
message = "".join(intSamples[0])
print(len(message))
print(message[0:10])