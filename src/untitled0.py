import numpy as np
from scipy.io import wavfile
import scipy.signal as sps




new_rate = 8192

    
sampling_rate, data = wavfile.read('C:/Users/Johan Gouws/Desktop/GenresDatabase - Copy/Rock/Dopamine-Blind_to_me.wav')
print(data.dtype)
number_of_samples = round(len(data) * float(new_rate) / sampling_rate)
data = sps.resample(data, number_of_samples)
data = data.astype(np.int16, order='C')
data = data[0:15000]

wavfile.write('Media/messageAudioDemo.wav',new_rate,data)
rate,samples = wavfile.read('Media/messageAudioDemo.wav')
print(max(samples))
#y,s = librosa.load('C:/Users/Johan Gouws/Desktop/GenresDatabase - Copy/Rock/__Copper__-Turn.wav', sr =8192) 
#y = y * 32768.0
#for i in range(0,len(y)):
#      y[i] = int(y[i])
#      
#scWave.write('Media/messageAudioDemo.wav',8192,y[50000:100000])
#rate,samples=scWave.read('Media/messageAudioDemo.wav')
#
#print(max(samples))


#username = open('UnamePword/username.txt', 'w')
#password = open('UnamePword/password.txt', 'w')
##
#username.write(AES.string2bits(AES.AESCipherCBC('admin').encrypt('admin')))
#password.write(AES.string2bits(AES.AESCipherCBC('admin').encrypt('admin')))
#username.close()
#password.close()
#
#
#
#username = open('UnamePword/username.txt', 'r')
#password = open('UnamePword/password.txt', 'r')
##
#userBits = username.read()
#pwdBits =  password.read()
#print(userBits)
#print(AES.bits2string(AES.decryptBinaryCBCString('0101100001101011011010100100100001010101010001100011011001001111011000110111101001000001001111010101011001010100011011110100101101110010011100100110011100111101', 'admin')))
#print((AES.AESCipherCBC('admin').decrypt(AES.bits2string(pwdBits))))
#username.close()
#password.close()

#import json
#from base64 import b64encode, b64decode
#from Crypto.Cipher import AES
#
#
#data = b"secret"
#
#key = b'\xa0\x9e([\x0f\x17\x0f\x11iG\x0b{\xc7\xf2\x91\xfd'
#cipher = AES.new(key, AES.MODE_CTR)
#ct_bytes = cipher.encrypt(data)
#nonce = b64encode(cipher.nonce).decode('utf-8')
#ct = b64encode(ct_bytes).decode('utf-8')
#result = json.dumps({'nonce':nonce, 'ciphertext':ct})
#
#try:
#    b64 = json.loads(result)
#    
#    nonce = b64decode(b64['nonce'])
#    print(b64['nonce'])
#    ct = b64decode(b64['ciphertext'])
#    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
#    pt = cipher.decrypt(ct)
#except (ValueError, KeyError):
#    print("Incorrect decryption")