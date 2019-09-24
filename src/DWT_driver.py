# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 13:51:31 2019

@author: project
"""

import pywt
import numpy as np
import wave
import fileprocessing as fp
import matplotlib.pyplot as plt
import dwtFirstPrinciples as firstP
import dwtLibrary
import dwtEncrypt
import scipy.io.wavfile as scWave
from copy import deepcopy
import ResultsAndTesting as RT



def school_round(a_in,n_in):
    if (a_in * 10 ** (n_in + 1)) % 10 == 5:
        return round(a_in + 1 / 10 ** (n_in + 1), n_in)
    else:
        return round(a_in, n_in)

testConvolution          = False
testLevelOneDWT          = False
testLevelsDWT            = False
plotDiffLevelCoeff       = False
plotUnderstanding        = False
plotCorrectImplemnt      = False
firstPrinciplesImplement = False
libraryImplement         = False
encryptDWTDriver         = True

def reconstruction_plot(yyy, **kwargs):
    """Plot signal vector on x [0,1] independently of amount of values it contains."""
    ym = np.median(yyy)
    plt.plot(np.linspace(0, 1., num=len(yyy)), yyy-ym, **kwargs)
    
def reconstruction_stem(yyy, xmax, **kwargs):
    """Plot coefficient vector on x [0,1] independently of amount of values it contains."""
    ymax = yyy.max()
    plt.stem(np.linspace(0, 1., num=len(yyy)), yyy*(xmax/ymax), use_line_collection = True, **kwargs)

###############################################################################
########################   Testing the convolution function  ##################
###############################################################################

if (testConvolution == True):
    
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
if (testLevelOneDWT == True):

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

if (testLevelsDWT == True):
    
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
        
###############################################################################
#############           Plotting significant plots           ##################
###############################################################################
if (plotDiffLevelCoeff == True):

    plotDiffLevelCoeff  = False    
    signal = pywt.data.ecg()
    wavletType = pywt.Wavelet('haar')
    levels = 6
    
    
    # cA_6 is the approximation coefficients at the sixth level
    # CD_6 is the detail coefficients at the sixth level
    # CD_5 is the detail coefficients at the sixth level
    # CD_4 is the detail coefficients at the sixth level
    # CD_3 is the detail coefficients at the sixth level
    # CD_2 is the detail coefficients at the sixth level
    # CD_1 is the detail coefficients at the sixth level
    cA_6, cD_6, cD_5, cD_4, cD_3, cD_2, cD_1 = pywt.wavedec(signal, wavletType, level=6)
    
    
    print("Number of samples:", len(signal))
    print("Length of cD_1", len(cD_1))
    print("Length of cD_2", len(cD_2))
    print("Length of cD_3", len(cD_3))
    print("Length of cD_4", len(cD_4))
    print("Length of cD_5", len(cD_5))
    print("Length of cD_6", len(cD_6))
    print("Length of cA_6", len(cA_6))
    
    
    
    xmax = signal.max()
    
    plt.figure()
    reconstruction_plot(signal)
    reconstruction_plot(pywt.waverec([cA_6, cD_6] + [None] * 5, wavletType))
    reconstruction_stem(cD_6, xmax, markerfmt ='none', linefmt='r-')
    plt.legend(['Original',('Rec to lvl 6'), ('Details for lvl 6')])
    
    plt.figure()
    reconstruction_plot(signal)
    reconstruction_plot(pywt.waverec([cA_6, cD_6, cD_5] + [None] * 4, wavletType))
    reconstruction_stem(cD_5, xmax, markerfmt ='none', linefmt='r-')
    plt.legend(['Original',('Rec to lvl 5'), ('Details for lvl 5')])
    
    plt.figure()
    reconstruction_plot(signal)
    reconstruction_plot(pywt.waverec([cA_6, cD_6, cD_5, cD_4] + [None] * 3, wavletType))
    reconstruction_stem(cD_4, xmax, markerfmt ='none', linefmt='r-')
    plt.legend(['Original',('Rec to lvl 4'),  ('Details for lvl 4')])
    
    plt.figure()
    reconstruction_plot(signal)
    reconstruction_plot(pywt.waverec([cA_6, cD_6, cD_5, cD_4, cD_3] + [None] * 2, wavletType))
    reconstruction_stem(cD_3, xmax, markerfmt ='none', linefmt='r-')
    plt.legend(['Original',('Rec to lvl 3'), ('Details for lvl 3')])
    
    plt.figure()
    reconstruction_plot(signal)
    reconstruction_plot(pywt.waverec([cA_6, cD_6, cD_5, cD_4, cD_3, cD_2] + [None] * 1, wavletType))
    reconstruction_stem(cD_2, xmax, markerfmt ='none', linefmt='r-')
    plt.legend(['Original',('Rec to lvl 2'), ('Details for lvl 2')])
    
    plt.figure()
    reconstruction_plot(signal)
    reconstruction_plot(pywt.waverec([cA_6, cD_6, cD_5, cD_4, cD_3, cD_2, cD_1] + [None] * 0, wavletType))
    reconstruction_stem(cD_1, xmax, markerfmt ='none', linefmt='r-')
    plt.legend(['Original', ('Rec to lvl 1'),  ('Details for lvl 1')])

    
    
if (plotUnderstanding == True):
    x = np.linspace(0, 1, num=2048)
    chirp_signal = np.sin(250 * np.pi * x**2)
        
    fig, ax = plt.subplots(figsize=(6,1))
    ax.set_title("Original Chirp Signal: ")
    ax.plot(chirp_signal)
    plt.show()
        
    data = chirp_signal
    waveletname = 'haar'
    
    fig, axarr = plt.subplots(nrows=5, ncols=2, figsize=(6,6))
    figR, axarrR = plt.subplots(nrows=5, ncols=1,figsize=(6,6))
    
    for ii in range(5):
        (data, coeff_d) = pywt.dwt(data, waveletname)
        axarr[ii, 0].plot(data, 'r')
        axarr[ii, 1].plot(coeff_d, 'g')
        axarr[ii, 0].set_ylabel("Level {}".format(ii + 1), fontsize=14, rotation=90)
        axarr[ii, 0].set_yticklabels([])
        axarrR[ii].plot(pywt.idwt(data, coeff_d, waveletname))
        axarrR[ii].set_title("Reconstruction of level " + str(ii+1) + " coefficients")
        if ii == 0:
            axarr[ii, 0].set_title("Approximation coefficients", fontsize=14)
            axarr[ii, 1].set_title("Detail coefficients", fontsize=14)
        axarr[ii, 1].set_yticklabels([])
    plt.tight_layout()
    plt.show()
    
if (plotCorrectImplemnt == True):
    # Create wavelet and extract the filters
    wavelet_name = 'haar'
    wavelet = pywt.Wavelet(wavelet_name)
    dec_lo, dec_hi, rec_lo, rec_hi = wavelet.filter_bank
    
    print("######################################################################")
    print("#########  Step one: Get the filter coefficients for haar:   #########")
    print("######################################################################")
    print("")
    print("Decomposing coefficients low .....", dec_lo)
    print("Decomposing coefficients high ....", dec_hi)
    print("Reconstruction coefficients low ..", rec_lo)
    print("Reconstruction coefficients high ..", rec_hi)
   
    # Filter coefficients
    plt.figure()
    plt.subplot(221)
    plt.stem(dec_lo, use_line_collection=True)
    plt.grid()
    plt.title('{} low-pass decomposition filter'.format(wavelet_name))
    
    plt.subplot(222)
    plt.stem(dec_hi, use_line_collection=True)
    plt.grid()
    plt.title('{} high-pass decomposition filter'.format(wavelet_name))
    plt.subplot(223)
    plt.stem(rec_lo, use_line_collection=True)
    plt.grid()
    plt.title('{} low-pass reconstruction filter'.format(wavelet_name))
    plt.subplot(224)
    plt.stem(rec_hi, use_line_collection=True)
    plt.grid()
    plt.title('{} high-pass reconstruction filter'.format(wavelet_name))
    
    # Frequency responses
    dec_lo_fr = np.abs(np.fft.fft(dec_lo, 128))
    dec_hi_fr = np.abs(np.fft.fft(dec_hi, 128))
    rec_lo_fr = np.abs(np.fft.fft(rec_lo, 128))
    rec_hi_fr = np.abs(np.fft.fft(rec_hi, 128))
    
    plt.figure()
    plt.subplot(211)
    plt.plot(dec_lo_fr, label='Low-pass')
    plt.plot(dec_hi_fr, label='High-pass')
    plt.grid()
    plt.legend()
    plt.title('Frequency responses of {} decomposition filters'.format(wavelet_name))
    plt.subplot(212)
    plt.plot(rec_lo_fr, label='Low-pass')
    plt.plot(rec_hi_fr, label='High-pass')
    plt.grid()
    plt.legend()
    plt.title('Frequency responses of {} reconstruction filters'.format(wavelet_name))
    
    plt.show()
    t = np.linspace(0, 1.0, 128*2*2*2)
    x = pywt.data.ecg()
    plt.figure()
    plt.plot(t,x)
    
    
    
if (firstPrinciplesImplement == True):
      # Open the cover audio
      song = wave.open('Media/song.wav', mode='rb')
      
      print("Getting cover samples")
      
      # Extract the wave samples from the host signal
      samplesOne, samplesTwo = fp.extractWaveSamples(song)
      
      print("Getting message samples")
      
      # Message to embed
      message = fp.getMessageBits('Media/opera.wav')
      message = "".join(list(map(str, message)))
      
      print("Encoding")
      
      stegoSamples, samplesUsed = firstP.dwtHaarEncode(samplesOne, message, 0, 2048, ".wav")
            
      print("Writing to stego")
      
      # Write to the stego song file
      fp.writeStegoToFile('Media/DWT.wav',song.getparams(), stegoSamples)
      
      print("Reading from stego")
      # Open the cover audio
      stego = wave.open('Media/DWT.wav', mode='rb')
      
      # Extract the wave samples from the host signal
      samplesOneStego, samplesTwoStego = fp.extractWaveSamples(stego)
      
      print("Extracting")
      
      extractMessage, fileType = firstP.dwtHaarDecode(samplesOneStego, 0, 2048)
          
      print("Writing to message file")
      fp.writeMessageBitsToFile(extractMessage, 'Media/dwtFirstPrinciplesMessageExtract.wav')
      
if (libraryImplement == True):
      # Open the cover audio
      song = wave.open('Media/song.wav', mode='rb')
      
      print("Getting cover samples")
      
      # Extract the wave samples from the host signal
      samplesOne, samplesTwo = fp.extractWaveSamples(song)
      
      print("Getting message samples")
      
      # Message to embed
      message = fp.getMessageBits('Media/cat.jpeg')
      message = "".join(list(map(str, message)))
      
      print("Encoding")
      
      stegoSamples, numEmbedded = dwtLibrary.dwtHaarEncodingLibrary(samplesOne, message, 4, 2048)
            
      print("Writing to stego")
      
      # Write to the stego song file
      fp.writeStegoToFile('Media/DWT.wav',song.getparams(), stegoSamples)
      
      print("Reading from stego")
      # Open the cover audio
      stego = wave.open('Media/DWT.wav', mode='rb')
      
      # Extract the wave samples from the host signal
      samplesOneStego, samplesTwoStego = fp.extractWaveSamples(stego)
      
      print("Extracting")
      
      extractMessage = dwtLibrary.dwtHaarDecodeLibrary(samplesOneStego, 4, 2048)
          
      print("Writing to message file")
      fp.writeMessageBitsToFile(extractMessage, 'Media/dwtLibraryMessageExtract.jpeg')
      
if (encryptDWTDriver == True):
    myMessage = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    rate, samples = scWave.read('/home/johan/Desktop/Audio-Steganograpy/src/Media/opera.wav')
    song = wave.open('/home/johan/Desktop/Audio-Steganograpy/src/Media/opera.wav', 'rb')
    originalCoverSamples = deepcopy(samples)

    stegoSamples, samplesUsed = dwtEncrypt.dwtEncryptEncode(list(samples), myMessage, 2048, ".txt")
    
    stegoSamples = np.asarray(stegoSamples)
    stegoSamples = stegoSamples.astype(np.float32, order='C') / 32768.0
      
    scWave.write("papagaai.wav", rate, stegoSamples)

    rate, extractStegoSamples = scWave.read('papagaai.wav')
    extractStegoSamples = extractStegoSamples.astype(np.float64, order='C') * 32768.0
    
    boodskap, fileType = dwtEncrypt.dwtEncryptDecode(extractStegoSamples, 2048)
    print("SNR of " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], extractStegoSamples[0:samplesUsed] ), 2)))

    print(boodskap, fileType)
      