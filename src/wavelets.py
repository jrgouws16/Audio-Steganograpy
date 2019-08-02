# https://dsp.stackexchange.com/questions/47437/discrete-wavelet-transform-visualizing-relation-between-decomposed-detail-coef

import pywt
import pywt.data
import numpy as np
import matplotlib.pyplot as plt
import fileprocessing as fp
import wave


def round_school(x):
    i, f = divmod(x, 1)
    return int(i + ((f >= 0.5) if (x > 0) else (f > 0.5)))

def reconstruction_plot(yyy, **kwargs):
    """Plot signal vector on x [0,1] independently of amount of values it contains."""
    ym = np.median(yyy)
    plt.plot(np.linspace(0, 1., num=len(yyy)), yyy-ym, **kwargs)


def reconstruction_stem(yyy, xmax, **kwargs):
    """Plot coefficient vector on x [0,1] independently of amount of values it contains."""
    ymax = yyy.max()
    plt.stem(np.linspace(0, 1., num=len(yyy)), yyy*(xmax/ymax), **kwargs)
    
    
def hideMessage(audioName, message, stegoPath):
    
    waveObject = wave.open(audioName, 'rb')
    signal = fp.extractWaveSamples(waveObject)
    signal = np.asarray(signal[0])
    wavletType = pywt.Wavelet('haar')
    
    cA_6, cD_6, cD_5, cD_4, cD_3, cD_2, cD_1 = pywt.wavedec(signal, wavletType, level=6)
    
    # This carries the most amount of information, while cD_6 carries the least
    for i in range(0, len(message)):
        cD_6[i] = message[i] * 10

    modSignal = map(int, pywt.waverec([cA_6, cD_6, cD_5, cD_4, cD_3, cD_2, cD_1], wavletType))
    fp.writeStegoToFile(stegoPath, waveObject.getparams(), list(modSignal))

def extractedMessage(stegoName, messageLen):
    waveObject = wave.open(stegoName, 'rb')
    signal = fp.extractWaveSamples(waveObject)
    signal = np.asarray(signal[0])
    wavletType = pywt.Wavelet('haar')
    
    cA_6, cD_6, cD_5, cD_4, cD_3, cD_2, cD_1 = pywt.wavedec(signal, wavletType, level=6)
    message = []
    decimalMessage = []
    
    for i in range(0, messageLen):
        decimalMessage.append(round_school(cD_6[i]/10))
    
    for i in range(0,messageLen): 
        message.append(chr(decimalMessage[i]))
    
    message = "".join(message)

    print(message)


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


'''
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
'''


'''
import pywt
import numpy as np
import matplotlib.pyplot as plt
 
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


'''


'''
message = "1111111111111111111111"*50

message = fp.messageToBinary(message)

decimalMessage = []

for i in range(0, len(message), 8):
    decimalMessage.append(int(message[i:i+8],2))
    
hideMessage('Media/opera.wav', decimalMessage, 'C:/Users/project/Desktop/DWT_stego.wav')

extractedMessage('C:/Users/project/Desktop/DWT_stego.wav', len(decimalMessage))
'''
