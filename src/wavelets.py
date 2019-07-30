# https://dsp.stackexchange.com/questions/47437/discrete-wavelet-transform-visualizing-relation-between-decomposed-detail-coef

import pywt
import pywt.data
import numpy as np
import matplotlib.pyplot as plt
import fileprocessing as fp
import wave

plt.close('all')

def reconstruction_plot(yyy, **kwargs):
    """Plot signal vector on x [0,1] independently of amount of values it contains."""
    #plt.figure()
    #plt.plot(np.linspace(0, 1, len(yyy)), yyy, **kwargs)
    ym = np.median(yyy)
    plt.plot(np.linspace(0, 1., num=len(yyy)), yyy-ym, **kwargs)


def reconstruction_stem(yyy, xmax, **kwargs):
    """Plot coefficient vector on x [0,1] independently of amount of values it contains."""
    ymax = yyy.max()
    plt.stem(np.linspace(0, 1., num=len(yyy)), yyy*(xmax/ymax), **kwargs)

waveObject = wave.open('Media/opera.wav', 'rb')
x = fp.extractWaveSamples(waveObject)
x=np.asarray(x[0])

w = pywt.Wavelet('sym5')
nl = 6
coeffs = pywt.wavedec(x, w, level=nl)

print("Coeff gotten")
'''
plt.figure()
plt.stem(coeffs[1]); plt.legend(['Lvl 6 detail coefficients'])
plt.figure()
plt.stem(coeffs[2]); plt.legend(['Lvl 5 detail coefficients'])
plt.figure()
plt.stem(coeffs[3]); plt.legend(['Lvl 4 detail coefficients'])
plt.figure()
plt.stem(coeffs[4]); plt.legend(['Lvl 3 detail coefficients'])
plt.figure()
plt.stem(coeffs[5]); plt.legend(['Lvl 2 detail coefficients'])
plt.figure()
plt.stem(coeffs[6]); plt.legend(['Lvl 1 detail coefficients'])
'''

"""
xmax = x.max()
for i in range(nl):
    plt.figure()
    #reconstruction_plot(x) # original signal 
    reconstruction_plot(pywt.waverec(coeffs[:i+2] + [None] * (nl-i-1), w)) # partial reconstruction
    reconstruction_stem(coeffs[i+1], xmax, markerfmt ='none', linefmt='r-')
    plt.legend(['Original', ('Rec to lvl %d')%(nl-i), ('Details for lvl %d')%(nl-i)])
    #plt.legend(['Original', ('Rec to lvl %d')%(nl-i)])
    
"""    
print(len(coeffs[0]))
print(len(coeffs[1]))
print(len(coeffs[2]))
print(len(coeffs[3]))
print(len(coeffs[4]))
print(len(coeffs[5]))

plt.figure(55)
reconstruction_plot(pywt.waverec(coeffs + [None] * 6, w)) # partial reconstruction   
