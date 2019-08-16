# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 13:51:31 2019

@author: project
"""

import pywt
import numpy as np
import DWT_first_principles as firstP
import wave
import fileprocessing as fp


###############################################################################
########################   Testing the convolution function  ##################
###############################################################################
print("##############        CONVOLUTION TESTS            ##########")
for i in range(0,100):
    # Testing the convolution function
    x = np.random.randint(500, size = 100)
    y = np.random.randint(500, size = 100)
    
    
    convLib = np.convolve(x,y)
    myConv = firstP.convolve(x,y)
    
    for n in range(0,len(convLib)):
        if (convLib[n] != myConv[n]):
            print("Convolution failed at test", str(i + 1))
            break            
    
        if (i == 99 and n ==99):
            print("Convolution successful in 100 tests")
            
print("")
            
###############################################################################
#############   Testing coeff generation level 1 vs library  ##################
###############################################################################
print("#############      Testing level 1                 ########\n")
levels = 1

# Open the cover audio
song = wave.open('Media/opera.wav', mode='rb')

# Extract the wave samples from the host signal
samplesOne, samplesTwo = fp.extractWaveSamples(song)

# Make the signal equal to block to process
while (len(samplesOne) % 1024 != 0):
    samplesOne.pop()

a, d = firstP.getLevelCoefficients(levels ,samplesOne)


aLib, dLib = pywt.wavedec(samplesOne, pywt.Wavelet('haar'), level = levels)


apprDiff = []
detlDiff = []
signalDifferences = []

for i in range(0, len(aLib)):
    if (i == len(a) or i == len(aLib) or i == len(d[0]) or i == len(dLib)):
        break
    apprDiff.append(np.abs(a[i] - aLib[i]))
    detlDiff.append(np.abs(d[0][i] - dLib[i]))

signal = firstP.getLevelSignal(a,d)
for i in range(len(samplesOne)):
    signalDifferences.append(np.abs(signal[i] - samplesOne[i]))
    
print("Max ampl diff of a reconstructed sample from original sample is " + str(max(signalDifferences)))
print("Max ampl diff of appr coeff of library and our implemntation " + str(max(apprDiff)))
print("Max ampl diff of det coeff of library and our implemntation " + str(max(detlDiff)))

print('')
###############################################################################
#############   Testing coeff generation for more levels     ##################
###############################################################################

for levels in range(2,6):
    print("#############      Testing level", levels, "DWT #################\n")
    coeff = firstP.getLevelCoefficients(levels, samplesOne)
    coeffLib = pywt.wavedec(samplesOne, pywt.Wavelet('haar'), level = levels)
    
    apprDiff = []
    detlDiff = []
    signalDifferences = []
    
    for i in range(0, len(coeff[0])):
        apprDiff.append(np.abs(coeff[0][i] - coeffLib[0][i]))
        
    print("Max ampl diff of appr coeff of library and our implemntation " + str(max(apprDiff)))
    
    tempDifferences = []
    for i in range(0, len(coeff[1])):
        for j in range(0, len(coeff[1][i])):
            tempDifferences.append(np.abs(coeffLib[i+1][j] - coeff[1][i][j]))
        print("Max ampl diff of det coeff of library and our implemntation (level " + str(len(coeff[1]) - i) + ") " + str(max(tempDifferences)))
        tempDifferences = []
    
    signal = firstP.getLevelSignal(coeff[0],coeff[1])
    for i in range(len(samplesOne)):
        signalDifferences.append(np.abs(signal[i] - samplesOne[i]))
        
    print("Max ampl diff of a reconstructed sample from original sample is " + str(max(signalDifferences)))
    print('')
    
    