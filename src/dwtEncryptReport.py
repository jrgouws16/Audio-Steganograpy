import ResultsAndTesting as RT
import dwtEncrypt
import fileprocessing as fp
import numpy as np
import matplotlib.pyplot as plt

import scipy.io.wavfile as scWave
from copy import deepcopy
import time
import os
import AES


allPaths = ['C:/Users/Johan Gouws/Desktop/GenresDatabase/Alternative',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Blues',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Electronic',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Jazz',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Pop',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Rock']

numSongsPerGenre = 100

for audioOrText in [False]:
      
      belowSNR  = [0, 0, 0, 0, 0, 0]
      
      totalEncodingTime = 0
      totalDecodingTime = 0
      
      SNRAlt = 0
      SNRBlu = 0
      SNREle = 0
      SNRJzz = 0
      SNRPop = 0
      SNRRoc = 0
      
      CapAlt = 0
      CapBlu = 0
      CapEle = 0
      CapJzz = 0
      CapPop = 0
      CapRoc = 0
      
      PRDAlt = 0
      PRDBlu = 0
      PRDEle = 0
      PRDJzz = 0
      PRDPop = 0
      PRDRoc = 0
      
      SPCCAlt = 0
      SPCCBlu = 0
      SPCCEle = 0
      SPCCJzz = 0
      SPCCPop = 0
      SPCCRoc = 0
      
      MSEAlt = 0
      MSEBlu = 0
      MSEEle = 0
      MSEJzz = 0
      MSEPop = 0
      MSERoc = 0
      
      PSNRAlt = 0
      PSNRBlu = 0
      PSNREle = 0
      PSNRJzz = 0
      PSNRPop = 0
      PSNRRoc = 0
      
      messageErrors = 0
      
      counter = numSongsPerGenre * 6
      
      for path in allPaths:
            coverFiles = []
                
            for r, d, f in os.walk(path):
              for file in f:
                  if '.wav' in file:
                      coverFiles.append(os.path.join(r, file))
      
      
            coverFiles = coverFiles[0:numSongsPerGenre]
                  
            for t in coverFiles:
                  samplesOne, samplesTwo, rate = fp.getWaveSamples(t)
                                      
                  message = ""
                  
                  if (audioOrText == True):
                        messageObject = open('C:/Users/Johan Gouws/Desktop/Audio-Steganograpy/src/Media/text.txt', "r")
                            
                        # Extract the message as a string of characters
                        message = messageObject.read()
                        messageObject.close()
                        
                  else:
                        # Get the audio samples in integer form
                        intSamples = fp.extractWaveMessage('C:/Users/Johan Gouws/Desktop/Audio-Steganograpy/src/Media/ShortOpera.wav')
                        
                        # Convert to integer list of bits for embedding
                        message = "".join(intSamples[0])
                        alphaMessage = ''
                        
                        # Convert the binary stream to a ASCII string
                        for i in range(0, len(message), 4):
                              alphaMessage += AES.bits2string('0010' + message[i: i + 4])
                              
                        message = alphaMessage
                                          
                  originalCoverSamples = deepcopy(samplesOne)
                  originalMessage = deepcopy(message)
                  
                  currentTime = time.time()
                  stegoSamples, samplesUsed, capacityWarning = dwtEncrypt.dwtEncryptEncode(samplesOne, message, 512, '.txt')        
                  embeddingTime = time.time() - currentTime
                  
                  totalEncodingTime += embeddingTime               
                  
                  if (capacityWarning == True):
                        print("Whoah the capacity is too small of the cover file")
                  
                  stegoSamples = np.asarray(stegoSamples, dtype=np.float32, order = 'C')/ 32768.0
                  scWave.write("Stego1.wav", rate, stegoSamples)
                                     
                  # Extract the samples from the stego file
                  stegoSamplesOne, stegoSamplesTwo, rate = fp.getWaveSamples("Stego1.wav")
                  stegoSamples = np.asarray(stegoSamplesOne, dtype=np.float32, order = 'C') * 32768.0
                  
                  
                  newTime = time.time()
                  secretMessage, fileType = dwtEncrypt.dwtEncryptDecode(list(stegoSamples), 512)
                  totalDecodingTime += time.time() - newTime
                  
                  
                  if (originalMessage != secretMessage):
                        messageErrors += 1      
                        print(t)
                  
                  SNR = RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] )
                  capacity = RT.getCapacity(message*8, samplesUsed, rate)
                  spcc = RT.getSPCC(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed])
                  mse = RT.getMSE(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed])
                  prd = RT.getPRD(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed])
                  psnr = RT.getPSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed])
        
                  print(counter, end=" ")
                  counter -= 1                  
                  
                 
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Alternative'):
                       SNRAlt += SNR
                       CapAlt += capacity
                       PRDAlt += prd
                       SPCCAlt += spcc
                       MSEAlt += mse
                       PSNRAlt += psnr

                       if (SNR < 20):
                             belowSNR[0] += 1
                                           
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Blues'):
                       SNRBlu += SNR
                       CapBlu += capacity
                       PRDBlu += prd
                       SPCCBlu += spcc
                       MSEBlu += mse
                       PSNRBlu += psnr

                       if (SNR < 20):
                             belowSNR[1] += 1

                       
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Electronic'):
                       SNREle += SNR
                       CapEle += capacity
                       PRDEle += prd
                       SPCCEle += spcc
                       MSEEle += mse
                       PSNREle += psnr

                       if (SNR < 20):
                             belowSNR[2] += 1
                     
                             
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Jazz'):
                       SNRJzz += SNR
                       CapJzz += capacity
                       PRDJzz += prd
                       SPCCJzz += spcc
                       MSEJzz += mse
                       PSNRJzz += psnr

                       if (SNR < 20):
                             belowSNR[3] += 1

                    
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Pop'):
                       SNRPop += SNR
                       CapPop += capacity
                       PRDPop += prd
                       SPCCPop += spcc
                       MSEPop += mse
                       PSNRPop += psnr

                       if (SNR < 20):
                             belowSNR[4] += 1
                       
                  if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Rock'):
                       SNRRoc += SNR
                       CapRoc += capacity
                       PRDRoc += prd
                       SPCCRoc += spcc
                       MSERoc += mse
                       PSNRRoc += psnr
                       
                       if (SNR < 20):
                             belowSNR[5] += 1
                       
                       
                             
      x = ['Alternative','Blues','Electronic','Jazz','Pop','Rock']
      x = np.asarray(x)       
      
      if (audioOrText == True):
            print("########################################################")
            print("##############   TEXT MESSAGE INFORMATION ##############")
            print("########################################################")
            plt.figure(25)
            plt.grid()
            plt.xlabel('Song genre')
            plt.ylabel('SNR (dB)')
            plt.plot(x, [SNRAlt/numSongsPerGenre,SNRBlu/numSongsPerGenre,SNREle/numSongsPerGenre,SNRJzz/numSongsPerGenre,SNRPop/numSongsPerGenre,SNRRoc/numSongsPerGenre])
            plt.figure(26)
            plt.grid()
            plt.xlabel('Song genre')
            plt.ylabel('PRD')
            plt.plot(x, [PRDAlt/numSongsPerGenre,PRDBlu/numSongsPerGenre,PRDEle/numSongsPerGenre,PRDJzz/numSongsPerGenre,PRDPop/numSongsPerGenre,PRDRoc/numSongsPerGenre])
            plt.figure(27)
            plt.grid()
            plt.xlabel('Song genre')
            plt.ylabel('SPCC')
            plt.plot(x, [SPCCAlt/numSongsPerGenre,SPCCBlu/numSongsPerGenre,SPCCEle/numSongsPerGenre,SPCCJzz/numSongsPerGenre,SPCCPop/numSongsPerGenre,SPCCRoc/numSongsPerGenre])
            plt.figure(28)
            plt.grid()
            plt.xlabel('Song genre')
            plt.ylabel('MSE')
            plt.plot(x, [MSEAlt/numSongsPerGenre,MSEBlu/numSongsPerGenre,MSEEle/numSongsPerGenre,MSEJzz/numSongsPerGenre,MSEPop/numSongsPerGenre,MSERoc/numSongsPerGenre])
            plt.figure(29)
            plt.grid()
            plt.xlabel('Song genre')
            plt.ylabel('PSNR (dB)')
            plt.plot(x, [PSNRAlt/numSongsPerGenre,PSNRBlu/numSongsPerGenre,PSNREle/numSongsPerGenre,PSNRJzz/numSongsPerGenre,PSNRPop/numSongsPerGenre,PSNRRoc/numSongsPerGenre])
            plt.figure(30)
            plt.grid()
            plt.xlabel('Song genre')
            plt.ylabel('Capacity (bits per 16 bit cover sample)')
            plt.plot(x, [CapAlt*1000/44100/numSongsPerGenre,CapBlu*1000/44100/numSongsPerGenre,CapEle*1000/44100/numSongsPerGenre,CapJzz*1000/44100/numSongsPerGenre,CapPop*1000/44100/numSongsPerGenre,CapRoc*1000/44100/numSongsPerGenre])
            
            print("#################  Statistics for the Encrypt encoding algorithm     #############")
            print("--------  SNR  ")
            print("# Alterantive",SNRAlt/numSongsPerGenre)
            print("# Blues      ",SNRBlu/numSongsPerGenre)
            print("# Electronic ",SNREle/numSongsPerGenre)
            print("# Jazz       ",SNRJzz/numSongsPerGenre)
            print("# Pop        ",SNRPop/numSongsPerGenre)
            print("# Rock       ",SNRRoc/numSongsPerGenre)   
            print("# Average    ",(SNRAlt/numSongsPerGenre + SNRBlu/numSongsPerGenre + SNREle/numSongsPerGenre + SNRJzz/numSongsPerGenre + SNRPop/numSongsPerGenre + SNRRoc/numSongsPerGenre)/6)      
            print("--------  PRD  ")
            print("# Alterantive",PRDAlt/numSongsPerGenre)
            print("# Blues      ",PRDBlu/numSongsPerGenre)
            print("# Electronic ",PRDEle/numSongsPerGenre)
            print("# Jazz       ",PRDJzz/numSongsPerGenre)
            print("# Pop        ",PRDPop/numSongsPerGenre)
            print("# Rock       ",PRDRoc/numSongsPerGenre)   
            print("# Average    ",(PRDAlt/numSongsPerGenre + PRDBlu/numSongsPerGenre + PRDEle/numSongsPerGenre + PRDJzz/numSongsPerGenre + PRDPop/numSongsPerGenre + PRDRoc/numSongsPerGenre)/6)      
            print("--------  SPCC  ")
            print("# Alterantive",SPCCAlt/numSongsPerGenre)
            print("# Blues      ",SPCCBlu/numSongsPerGenre)
            print("# Electronic ",SPCCEle/numSongsPerGenre)
            print("# Jazz       ",SPCCJzz/numSongsPerGenre)
            print("# Pop        ",SPCCPop/numSongsPerGenre)
            print("# Rock       ",SPCCRoc/numSongsPerGenre)   
            print("# Average    ",(SPCCAlt/numSongsPerGenre + SPCCBlu/numSongsPerGenre + SPCCEle/numSongsPerGenre + SPCCJzz/numSongsPerGenre + SPCCPop/numSongsPerGenre + SPCCRoc/numSongsPerGenre)/6)      
            print("--------  MSE  ")
            print("# Alterantive",MSEAlt/numSongsPerGenre)
            print("# Blues      ",MSEBlu/numSongsPerGenre)
            print("# Electronic ",MSEEle/numSongsPerGenre)
            print("# Jazz       ",MSEJzz/numSongsPerGenre)
            print("# Pop        ",MSEPop/numSongsPerGenre)
            print("# Rock       ",MSERoc/numSongsPerGenre)   
            print("# Average    ",(MSEAlt/numSongsPerGenre + MSEBlu/numSongsPerGenre + MSEEle/numSongsPerGenre + MSEJzz/numSongsPerGenre + MSEPop/numSongsPerGenre + MSERoc/numSongsPerGenre)/6)      
            print("--------  PSNR  ")
            print("# Alterantive",PSNRAlt/numSongsPerGenre)
            print("# Blues      ",PSNRBlu/numSongsPerGenre)
            print("# Electronic ",PSNREle/numSongsPerGenre)
            print("# Jazz       ",PSNRJzz/numSongsPerGenre)
            print("# Pop        ",PSNRPop/numSongsPerGenre)
            print("# Rock       ",PSNRRoc/numSongsPerGenre)   
            print("# Average    ",(PSNRAlt/numSongsPerGenre + PSNRBlu/numSongsPerGenre + PSNREle/numSongsPerGenre + PSNRJzz/numSongsPerGenre + PSNRPop/numSongsPerGenre + PSNRRoc/numSongsPerGenre)/6)      
            print("--------  Capacity  ")
            print("# Alterantive",CapAlt*1000/44100/numSongsPerGenre)
            print("# Blues      ",CapBlu*1000/44100/numSongsPerGenre)
            print("# Electronic ",CapEle*1000/44100/numSongsPerGenre)
            print("# Jazz       ",CapJzz*1000/44100/numSongsPerGenre)
            print("# Pop        ",CapPop*1000/44100/numSongsPerGenre)
            print("# Rock       ",CapRoc*1000/44100/numSongsPerGenre)   
            print("# Average    ",(CapAlt*1000/44100/numSongsPerGenre + CapBlu*1000/44100/numSongsPerGenre + CapEle*1000/44100/numSongsPerGenre + CapJzz*1000/44100/numSongsPerGenre + CapPop*1000/44100/numSongsPerGenre + CapRoc*1000/44100/numSongsPerGenre)/6)      
            print("--------  Number of songs below SNR of 20 dB  ")
            print("# Alterantive",belowSNR[0])
            print("# Blues      ",belowSNR[1])
            print("# Electronic ",belowSNR[2])
            print("# Jazz       ",belowSNR[3])
            print("# Pop        ",belowSNR[4])
            print("# Rock       ",belowSNR[5])   
            print("# Average    ",(belowSNR[0]+belowSNR[1]+belowSNR[2]+belowSNR[3]+belowSNR[4]+belowSNR[5])/6)      
            print("--------  Average embedding time  ") 
            print("# Embedding Time    ",totalEncodingTime/(numSongsPerGenre * 6), "seconds")   
            
            print("#################  Statistics for the Encrypt extraction algorithm     #############")
            print("--------  Number of errors made with extraction", messageErrors) 
                  
            print("# Extraction Time    ",totalDecodingTime/(numSongsPerGenre * 6), "seconds")   
      
      else:
            print("########################################################")
            print("##############   Audio MESSAGE INFORMATION ##############")
            print("########################################################")
            plt.figure(31)
            plt.grid()
            plt.xlabel('Song genre')
            plt.ylabel('SNR (dB)')
            plt.plot(x, [SNRAlt/numSongsPerGenre,SNRBlu/numSongsPerGenre,SNREle/numSongsPerGenre,SNRJzz/numSongsPerGenre,SNRPop/numSongsPerGenre,SNRRoc/numSongsPerGenre])
            plt.figure(32)
            plt.grid()
            plt.xlabel('Song genre')
            plt.ylabel('PRD')
            plt.plot(x, [PRDAlt/numSongsPerGenre,PRDBlu/numSongsPerGenre,PRDEle/numSongsPerGenre,PRDJzz/numSongsPerGenre,PRDPop/numSongsPerGenre,PRDRoc/numSongsPerGenre])
            plt.figure(33)
            plt.grid()
            plt.xlabel('Song genre')
            plt.ylabel('SPCC')
            plt.plot(x, [SPCCAlt/numSongsPerGenre,SPCCBlu/numSongsPerGenre,SPCCEle/numSongsPerGenre,SPCCJzz/numSongsPerGenre,SPCCPop/numSongsPerGenre,SPCCRoc/numSongsPerGenre])
            plt.figure(34)
            plt.grid()
            plt.xlabel('Song genre')
            plt.ylabel('MSE')
            plt.plot(x, [MSEAlt/numSongsPerGenre,MSEBlu/numSongsPerGenre,MSEEle/numSongsPerGenre,MSEJzz/numSongsPerGenre,MSEPop/numSongsPerGenre,MSERoc/numSongsPerGenre])
            plt.figure(35)
            plt.grid()
            plt.xlabel('Song genre')
            plt.ylabel('PSNR (dB)')
            plt.plot(x, [PSNRAlt/numSongsPerGenre,PSNRBlu/numSongsPerGenre,PSNREle/numSongsPerGenre,PSNRJzz/numSongsPerGenre,PSNRPop/numSongsPerGenre,PSNRRoc/numSongsPerGenre])
            plt.figure(36)
            plt.grid()
            plt.xlabel('Song genre')
            plt.ylabel('Capacity (bits per 16 bit cover sample)')
            plt.plot(x, [CapAlt*1000/44100/numSongsPerGenre,CapBlu*1000/44100/numSongsPerGenre,CapEle*1000/44100/numSongsPerGenre,CapJzz*1000/44100/numSongsPerGenre,CapPop*1000/44100/numSongsPerGenre,CapRoc*1000/44100/numSongsPerGenre])
            
            print("#################  Statistics for the Encrypt encoding algorithm     #############")
            print("--------  SNR  ")
            print("# Alterantive",SNRAlt/numSongsPerGenre)
            print("# Blues      ",SNRBlu/numSongsPerGenre)
            print("# Electronic ",SNREle/numSongsPerGenre)
            print("# Jazz       ",SNRJzz/numSongsPerGenre)
            print("# Pop        ",SNRPop/numSongsPerGenre)
            print("# Rock       ",SNRRoc/numSongsPerGenre)   
            print("# Average    ",(SNRAlt/numSongsPerGenre + SNRBlu/numSongsPerGenre + SNREle/numSongsPerGenre + SNRJzz/numSongsPerGenre + SNRPop/numSongsPerGenre + SNRRoc/numSongsPerGenre)/6)      
            print("--------  PRD  ")
            print("# Alterantive",PRDAlt/numSongsPerGenre)
            print("# Blues      ",PRDBlu/numSongsPerGenre)
            print("# Electronic ",PRDEle/numSongsPerGenre)
            print("# Jazz       ",PRDJzz/numSongsPerGenre)
            print("# Pop        ",PRDPop/numSongsPerGenre)
            print("# Rock       ",PRDRoc/numSongsPerGenre)   
            print("# Average    ",(PRDAlt/numSongsPerGenre + PRDBlu/numSongsPerGenre + PRDEle/numSongsPerGenre + PRDJzz/numSongsPerGenre + PRDPop/numSongsPerGenre + PRDRoc/numSongsPerGenre)/6)      
            print("--------  SPCC  ")
            print("# Alterantive",SPCCAlt/numSongsPerGenre)
            print("# Blues      ",SPCCBlu/numSongsPerGenre)
            print("# Electronic ",SPCCEle/numSongsPerGenre)
            print("# Jazz       ",SPCCJzz/numSongsPerGenre)
            print("# Pop        ",SPCCPop/numSongsPerGenre)
            print("# Rock       ",SPCCRoc/numSongsPerGenre)   
            print("# Average    ",(SPCCAlt/numSongsPerGenre + SPCCBlu/numSongsPerGenre + SPCCEle/numSongsPerGenre + SPCCJzz/numSongsPerGenre + SPCCPop/numSongsPerGenre + SPCCRoc/numSongsPerGenre)/6)      
            print("--------  MSE  ")
            print("# Alterantive",MSEAlt/numSongsPerGenre)
            print("# Blues      ",MSEBlu/numSongsPerGenre)
            print("# Electronic ",MSEEle/numSongsPerGenre)
            print("# Jazz       ",MSEJzz/numSongsPerGenre)
            print("# Pop        ",MSEPop/numSongsPerGenre)
            print("# Rock       ",MSERoc/numSongsPerGenre)   
            print("# Average    ",(MSEAlt/numSongsPerGenre + MSEBlu/numSongsPerGenre + MSEEle/numSongsPerGenre + MSEJzz/numSongsPerGenre + MSEPop/numSongsPerGenre + MSERoc/numSongsPerGenre)/6)      
            print("--------  PSNR  ")
            print("# Alterantive",PSNRAlt/numSongsPerGenre)
            print("# Blues      ",PSNRBlu/numSongsPerGenre)
            print("# Electronic ",PSNREle/numSongsPerGenre)
            print("# Jazz       ",PSNRJzz/numSongsPerGenre)
            print("# Pop        ",PSNRPop/numSongsPerGenre)
            print("# Rock       ",PSNRRoc/numSongsPerGenre)   
            print("# Average    ",(PSNRAlt/numSongsPerGenre + PSNRBlu/numSongsPerGenre + PSNREle/numSongsPerGenre + PSNRJzz/numSongsPerGenre + PSNRPop/numSongsPerGenre + PSNRRoc/numSongsPerGenre)/6)      
            print("--------  Capacity  ")
            print("# Alterantive",CapAlt*1000/44100/numSongsPerGenre)
            print("# Blues      ",CapBlu*1000/44100/numSongsPerGenre)
            print("# Electronic ",CapEle*1000/44100/numSongsPerGenre)
            print("# Jazz       ",CapJzz*1000/44100/numSongsPerGenre)
            print("# Pop        ",CapPop*1000/44100/numSongsPerGenre)
            print("# Rock       ",CapRoc*1000/44100/numSongsPerGenre)   
            print("# Average    ",(CapAlt*1000/44100/numSongsPerGenre + CapBlu*1000/44100/numSongsPerGenre + CapEle*1000/44100/numSongsPerGenre + CapJzz*1000/44100/numSongsPerGenre + CapPop*1000/44100/numSongsPerGenre + CapRoc*1000/44100/numSongsPerGenre)/6)      
            print("--------  Number of songs below SNR of 20 dB  ")
            print("# Alterantive",belowSNR[0])
            print("# Blues      ",belowSNR[1])
            print("# Electronic ",belowSNR[2])
            print("# Jazz       ",belowSNR[3])
            print("# Pop        ",belowSNR[4])
            print("# Rock       ",belowSNR[5])   
            print("# Average    ",(belowSNR[0]+belowSNR[1]+belowSNR[2]+belowSNR[3]+belowSNR[4]+belowSNR[5])/6)      
            print("--------  Average embedding time  ") 
            print("# Embedding Time    ",totalEncodingTime/(numSongsPerGenre * 6), "seconds")   
            
            print("#################  Statistics for the Encrypt extraction algorithm     #############")
            print("--------  Number of errors made with extraction", messageErrors) 
                  
            print("# Extraction Time    ",totalDecodingTime/(numSongsPerGenre * 6), "seconds")   
