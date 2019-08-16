# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:19:34 2019

@author: project
"""

import numpy as np
import fileprocessing as fp
import wave

# Convolve signal x with signal y
def convolve(x, y):
    lenX = len(x)
    lenY = len(y)
    
    reversedY = np.asarray(y[::-1])
    x = np.asarray(x)
    
    convolved = []
    
    # Before the shifting signal moved over the stationary signal
    for i in range(0, lenY - 1):
        convolved.append(sum(reversedY[-i-1:] * x[:i + 1]))
    
    # While the shifting signal moves over the stationary signal
    for i in range(0, lenX - lenY + 1):
        convolved.append(sum(reversedY * x[i:i + lenY]))
        
    # While the shifting signal is moving over the stationary signal    
    for i in range(0, lenY - 1):
        convolved.append(sum(reversedY[:-i-1] * x[lenX - lenY + i + 1:]))
        
    return convolved

# Takes as input the signal and returns the approximation coefficients
# and detailed coefficients
def getCoeff(signal):
    # Haar coefficients for low pass filter decomposition
    coefLowDec  = [0.7071067811865476,  0.7071067811865476]
    
    # Haar coefficients for high pass filter decomposition
    coefHighDec = [-0.7071067811865476, 0.7071067811865476]

    # Convolve the signal with the low-pass for the approximation coefficients
    approx = convolve(signal, coefLowDec)
    approx = approx[1::2]

    # Convolve the signal with the high-pass for the detailed coefficients
    detail = convolve(signal, coefHighDec)
    detail = detail[1::2]
    return approx, detail

def getSignal(approx, detail):
    # Haar coefficients for low pass filter reconstruction
    coefLowRec  = [0.7071067811865476,  0.7071067811865476]
    
    # Haar coefficients for high pass filter reconstruction
    coefHighRec = [0.7071067811865476, -0.7071067811865476]
    
    # using itertool.chain() 
    # inserting K after every Nth number  
    for b in range (0,len(approx)):
        approx.insert(b*2,0)

    for b in range (0,len(detail)):
        detail.insert(b*2,0)

    del detail[0]
    del approx[0]

    #detail.append(0)
    #approx.append(0)    

    approxSignal = convolve(approx, coefLowRec)
    detailSignal = convolve(detail, coefHighRec)
    
    while (len(approxSignal) < len(detailSignal)):
        approxSignal.append(0)
        
    while (len(approxSignal) > len(detailSignal)):
        detailSignal.append(0)
    
    approxSignal = np.asarray(approxSignal)
    detailSignal = np.asarray(detailSignal)
    
    
    returnList   = list(map(int, list(approxSignal + detailSignal)))
    return returnList
    
    
def getLevelCoefficients(levels, signal):
    approx = signal
    detail = []

    for i in range(0, levels):
        approx, det = getCoeff(approx)
        detail.insert(0, det)
    return approx, detail

def getLevelSignal(approx, detail):
    signal = approx
    
    for i in range(len(detail)):
        signal = getSignal(signal, detail[i])
       
    return signal
        




