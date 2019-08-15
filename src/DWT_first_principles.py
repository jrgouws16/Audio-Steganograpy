# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:19:34 2019

@author: project
"""

import numpy as np


# Convolve signal x with signal y
def convolve(x, y):
    lenX = len(x)
    lenY = len(y)
    
    reversedY = np.asarray(y[::-1])
    x = np.asarray(x)
    
    convolved = []
    
    for i in range(0, lenY - 1):
        convolved.append(sum(reversedY[-i-1:] * x[:i + 1]))
    
    for i in range(0, lenX - lenY + 1):
        convolved.append(sum(reversedY * x[i:i + lenY]))
        
    for i in range(0, lenY - 1):
        convolved.append(sum(reversedY[:-i-1] * x[lenX - lenY + i + 1:]))
        
    return convolved

# Haar coefficients for low pass filter decomposition
coefLowDec  = [0.7071067811865476,  0.7071067811865476]

# Haar coefficients for high pass filter decomposition
coefHighDec = [-0.7071067811865476, 0.7071067811865476]

# Haar coefficients for low pass filter reconstruction
coefLowRec  = [0.7071067811865476,  0.7071067811865476]

# Haar coefficients for high pass filter reconstruction
coefHighRec = [0.7071067811865476, -0.7071067811865476]

x = [-86,-87,-87,-89,-89,-90,-91,-93,-96,-97]
convolved = convolve(x, coefHighDec)
convolved = convolved[1::2]

correctConvolved = np.convolve(x,coefHighDec)
correctConvolved = correctConvolved[1::2]
print(convolved[0:10])
print(correctConvolved[0:10])
    