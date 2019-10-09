import fileprocessing as fp
import dwtEncrypt as DWTcrypt
import scipy.io.wavfile as scWave
import numpy as np
import AES

key = 'aesdsfdsfdsfdsfs'
fileType = '.txt'
samplesOne, samplesTwo, rate = fp.getWaveSamples("Media/opera.wav")
                    
message = ""

if (fileType == ".txt"):
     
      messageObject = open('Media/text.txt', "r")
    
      # Extract the message as a string of characters
      message = messageObject.read()
      message = AES.string2bits(message)
      message = AES.encryptBinaryString(message,key)
      message = AES.bits2string(message)
      
      messageObject.close()

message = AES.string2bits(message)
message = AES.decryptBinaryString(message,key)
message = AES.bits2string(message)
print(message)

#     
#stegoSamples, samplesUsed = DWTcrypt.dwtEncryptEncode(samplesOne, message, 2048, fileType)        
#stegoSamples = np.asarray(stegoSamples)
#stegoSamples = stegoSamples.astype(np.float32, order='C') / 32768.0
#scWave.write("testingAES.wav", rate, stegoSamples)
#
#
## Extract the samples from the stego file
#rate, samples = scWave.read("testingAES.wav")
#samples = samples.astype(np.float64, order='C') * 32768.0
#                        
#secretMessage, fileType = DWTcrypt.dwtEncryptDecode(list(samples), 2048)
#
#if (secretMessage == "WRONG_KEY"):
#      print("IN HERE")
#      fileType = '.txt'
#      secretMessage = fp.messageToBinary('Unauthorised access.\n Wrong AES password provided')
#      fp.writeMessageBitsToFile(secretMessage, 'Media/ted.txt')
#
#else:
#      messageFileObj = open('Media/ted.txt', 'w')
#      messageFileObj.write(secretMessage)
#      messageFileObj.close()
                                      
                    
