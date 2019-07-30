'''import wave

import pylab
def graph_spectrogram(wav_file):
    sound_info, frame_rate = get_wav_info(wav_file)
    pylab.figure(num=None, figsize=(19, 12))
    pylab.subplot(111)
    pylab.title('spectrogram of %r' % wav_file)
    pylab.specgram(sound_info, Fs=frame_rate)
    pylab.savefig('spectrogram.png')
    
def get_wav_info(wav_file):
    wav = wave.open(wav_file, 'r')
    frames = wav.readframes(-1)
    sound_info = pylab.fromstring(frames, 'int16')
    frame_rate = wav.getframerate()
    wav.close()
    return sound_info, frame_rate

graph_spectrogram('C:/Users/project/Desktop/Audio-Steganograpy/src/Media/StegoSong.wav')
'''

import pywt
import pywt.data
import numpy as np
import matplotlib.pyplot as plt

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


x = pywt.data.ecg()
w = pywt.Wavelet('sym5')
nl = 6
coeffs = pywt.wavedec(x, w, level=nl)


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


xmax = x.max()
for i in range(nl):
    plt.figure()
    reconstruction_plot(x) # original signal 
    reconstruction_plot(pywt.waverec(coeffs[:i+2] + [None] * (nl-i-1), w)) # partial reconstruction 
    #reconstruction_stem(coeffs[i+1], xmax, markerfmt ='none', linefmt='r-')
    #plt.legend(['Original', ('Rec to lvl %d')%(nl-i), ('Details for lvl %d')%(nl-i)])
    plt.legend(['Original', ('Rec to lvl %d')%(nl-i)])