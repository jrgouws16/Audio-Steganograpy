# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:19:34 2019

@author: project
"""

# https://dsp.stackexchange.com/questions/45758/programming-the-idwt-for-image-processing
# https://dsp.stackexchange.com/questions/47437/discrete-wavelet-transform-visualizing-relation-between-decomposed-detail-coef
# https://dsp.stackexchange.com/questions/48138/how-to-implement-a-filter-associated-to-a-specific-wavelet

import numpy as np
import math

# Inverse of the binary_representation function of numpy
def binaryToInt(binaryString):
       
    if (binaryString[0] == '1'):
        return int(binaryString, 2)-(1<<len(binaryString))
    else:
        return int(binaryString, 2)

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

# One level reconstruction of signal from coefficients
def getSignal(approx, detail):
    # Haar coefficients for low pass filter reconstruction
    coefLowRec  = [0.7071067811865476,  0.7071067811865476]
    
    # Haar coefficients for high pass filter reconstruction
    coefHighRec = [0.7071067811865476, -0.7071067811865476]
    
    # Insert zero's every second index, for upsampling, starting at index 0
    for b in range (0,len(approx)):
        approx.insert(b*2,0)

    for b in range (0,len(detail)):
        detail.insert(b*2,0)

    # First index should not be a zero
    del detail[0]
    del approx[0]
 
    # Convolve the coefficients with the filter coefficients
    approxSignal = convolve(approx, coefLowRec)
    detailSignal = convolve(detail, coefHighRec)
    
    # If they are of different lengths, make them of equal lengths
    while (len(approxSignal) < len(detailSignal)):
        approxSignal.append(0)
        
    while (len(approxSignal) > len(detailSignal)):
        detailSignal.append(0)
    
    approxSignal = np.asarray(approxSignal)
    detailSignal = np.asarray(detailSignal)
    
    # Add the results and return the result
    returnList   = list(map(float, list(approxSignal + detailSignal)))
    
    return returnList
    
# Function able to perform Haar DWT of level greater than one
def getLevelCoefficients(levels, signal):
    approx = signal
    detail = []

    for i in range(0, levels):
        approx, det = getCoeff(approx)
        detail.insert(0, det)
    return approx, detail

# Function able to perform Haar IDWT of level greater than one
# Takes approximation coefficients list as first parameter and list of 
# detailed coefficients lists as the second paramenter
def getLevelSignal(approx, detail):
    signal = approx
    
    for i in range(len(detail)):
        signal = getSignal(signal, detail[i])
       
    return signal
     
# Process block at a time and returns a list of approximate coeff and detail
# Coefficients in the form [[approximate[0], approximate[1]],[detail[0],detail[1]]]
def getCoefficients(samples, blockLength):
    blocks = int(len(samples) / blockLength)
    
    coefficients = [[],[]]

    for i in range(0, math.floor(blocks)):     
        cA_1, cD_1 = getCoeff(samples[i * blockLength: i * blockLength + blockLength])
        coefficients[0].append(cA_1)
        coefficients[1].append(cD_1)
            
    return coefficients


      





