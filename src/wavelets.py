# https://dsp.stackexchange.com/questions/47437/discrete-wavelet-transform-visualizing-relation-between-decomposed-detail-coef

import pywt
import pywt.data
import numpy as np
import matplotlib.pyplot as plt
import fileprocessing as fp
import wave
import scipy.fftpack


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

'''
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


# Create wavelet and extract the filters
wavelet_name = 'haar'
wavelet = pywt.Wavelet(wavelet_name)
dec_lo, dec_hi, rec_lo, rec_hi = wavelet.filter_bank
'''
print("######################################################################")
print("#########  Step one: Get the filter coefficients for haar:   #########")
print("######################################################################")
print("")
print("Decomposing coefficients low .....", dec_lo)
print("Decomposing coefficients high ....", dec_hi)
print("Reconstruction coefficients low ..", rec_lo)
print("Reconstruction coefficients high ..", rec_hi)
'''
'''
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
'''

'''
# Frequency responses
dec_lo_fr = np.abs(np.fft.fft(dec_lo, 128))
dec_hi_fr = np.abs(np.fft.fft(dec_hi, 128))
rec_lo_fr = np.abs(np.fft.fft(rec_lo, 128))
rec_hi_fr = np.abs(np.fft.fft(rec_hi, 128))



plt.figure()
plt.subplot(211)
plt.plot(dec_lo_fr, label='Low-pass')
#plt.hold(True)
plt.plot(dec_hi_fr, label='High-pass')
plt.grid()
plt.legend()
plt.title('Frequency responses of {} decomposition filters'.format(wavelet_name))
plt.subplot(212)
plt.plot(rec_lo_fr, label='Low-pass')
#plt.hold(True)
plt.plot(rec_hi_fr, label='High-pass')
plt.grid()
plt.legend()
plt.title('Frequency responses of {} reconstruction filters'.format(wavelet_name))

plt.show()
'''

#y = lfilter(dec_lo, 1, x)
#y = convolve(x, dec_lo)

t = np.linspace(0, 1.0, 128*2*2*2)
#x = np.sin(2*np.pi*10*t)
x = pywt.data.ecg()


print("xxxxxxxx", x[0:10])

plt.figure()
plt.plot(t,x)

wavletType = pywt.Wavelet('haar')
cA_1, cD_1 = pywt.wavedec(x, wavletType, level=1)

    
print("Convolved")
convolved = np.convolve([-86, -87, -87, -89, -89, -90, -91, -93, -96, -97], [-1/np.sqrt(2), 1/np.sqrt(2)])

for i in convolved:
    print(i)

# Perform manual DWT and decimate
cA = np.convolve(x, dec_lo)[1::2]
cD = np.convolve(x, dec_hi)[1::2]

    
plt.figure()
plt.subplot(211)
plt.plot(cA)
plt.grid()
plt.title('Approximation coefficients')

plt.subplot(212)
plt.plot(cD)
plt.grid()
plt.title('Detail coefficients')

plt.show()

message = "Is this actually working"

message = fp.messageToBinary(message)

decimalMessage = []

for i in range(0, len(message), 8):
    decimalMessage.append(int(message[i:i+8],2))
    
hideMessage('Media/opera.wav', decimalMessage, 'C:/Users/project/Desktop/DWT_stego.wav')

extractedMessage('C:/Users/project/Desktop/DWT_stego.wav', len(decimalMessage))

