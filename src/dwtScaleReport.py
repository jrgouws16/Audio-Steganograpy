import ResultsAndTesting as RT
import dwtScale
import fileprocessing as fp
import numpy as np
import matplotlib.pyplot as plt

import scipy.io.wavfile as scWave
from copy import deepcopy
import time
import os
import AES

textMessage = True

allPaths = ['C:/Users/Johan Gouws/Desktop/GenresDatabase/Alternative',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Blues',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Electronic',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Jazz',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Pop',
            'C:/Users/Johan Gouws/Desktop/GenresDatabase/Rock']

numSongsPerGenre = 100

x = ['Alternative','Blues','Electronic','Jazz','Pop','Rock']
x = np.asarray(x)

LSBs = [1,5,10,14]

for audioOrText in [False]:
      
      SNRAlt = [0]*len(LSBs)
      SNRBlu = [0]*len(LSBs)
      SNREle = [0]*len(LSBs)
      SNRJzz = [0]*len(LSBs)
      SNRPop = [0]*len(LSBs)
      SNRRoc = [0]*len(LSBs)
      
      CapAlt = [0]*len(LSBs)
      CapBlu = [0]*len(LSBs)
      CapEle = [0]*len(LSBs)
      CapJzz = [0]*len(LSBs)
      CapPop = [0]*len(LSBs)
      CapRoc = [0]*len(LSBs)
      
      PRDAlt = [0]*len(LSBs)
      PRDBlu = [0]*len(LSBs)
      PRDEle = [0]*len(LSBs)
      PRDJzz = [0]*len(LSBs)
      PRDPop = [0]*len(LSBs)
      PRDRoc = [0]*len(LSBs)
      
      SPCCAlt = [0]*len(LSBs)
      SPCCBlu = [0]*len(LSBs)
      SPCCEle = [0]*len(LSBs)
      SPCCJzz = [0]*len(LSBs)
      SPCCPop = [0]*len(LSBs)
      SPCCRoc = [0]*len(LSBs)
      
      MSEAlt = [0]*len(LSBs)
      MSEBlu = [0]*len(LSBs)
      MSEEle = [0]*len(LSBs)
      MSEJzz = [0]*len(LSBs)
      MSEPop = [0]*len(LSBs)
      MSERoc = [0]*len(LSBs)
      
      PSNRAlt = [0]*len(LSBs)
      PSNRBlu = [0]*len(LSBs)
      PSNREle = [0]*len(LSBs)
      PSNRJzz = [0]*len(LSBs)
      PSNRPop = [0]*len(LSBs)
      PSNRRoc = [0]*len(LSBs)
      
      belowSNR = []
      
      for i in range(6):
            belowSNR.append([0]*len(LSBs))
      
      totalEncodingTime = [0]*len(LSBs)
      totalDecodingTime = [0]*len(LSBs)
      
      
      messageErrors = 0
      
      counter = numSongsPerGenre * 6 *len(LSBs)
      capacityWarnings = 0
      
      for path in allPaths:
            coverFiles = []
                
            for r, d, f in os.walk(path):
              for file in f:
                  if '.wav' in file:
                      coverFiles.append(os.path.join(r, file))
      
      
            coverFiles = coverFiles[0:numSongsPerGenre]
                  
            for t in coverFiles:
                  for LSB_index in range(0, len(LSBs)):

                        AESkeyEncode = "THIS_IS_THE_KEY_USED_FOR_AES_ENCRYPTION"
                        
                        samplesOne, samplesTwo, rate = fp.getWaveSamples(t)
                        originalCoverSamples = deepcopy(samplesOne)
                        
                        if (audioOrText == True):
                              message = ""
                              message = fp.getMessageBits('C:/Users/Johan Gouws/Desktop/Audio-Steganograpy/src/Media/text.txt')
                              message = list(map(str, message))
                              message = "".join(message)
                              originalMessage = deepcopy(message)
                              message = AES.encryptBinaryString(message, AESkeyEncode)
                              message = list(map(int, list(message)))
                              message = "".join(list(map(str, message)))
                        
                        else:
                                       
                              # Get the audio samples in integer form
                              intSamples = fp.extractWaveMessage('C:/Users/Johan Gouws/Desktop/Audio-Steganograpy/src/Media/ShortOpera.wav')
                              
                              # Convert to integer list of bits for embedding
                              message = "".join(intSamples[0])
                              originalMessage = deepcopy(message)
                              message = AES.encryptBinaryString(message, AESkeyEncode)
                              message = list(map(int, list(message)))
                              message = "".join(list(map(str, message)))
                        
                        currentTime = time.time()
                        stegoSamples, samplesUsed, capacityWarning = dwtScale.dwtScaleEncode(samplesOne, message, '.txt', LSBs[LSB_index])
                        totalEncodingTime[LSB_index] += time.time() - currentTime
                        
                        
                        if (capacityWarning == True):
                              print("Whoah the capacity is too small of the cover file")
                        
                        stegoSamples = np.asarray(stegoSamples, dtype=np.float32, order = 'C')/ 32768.0
                        scWave.write("Stego2.wav", rate, stegoSamples)
                                           
                        # Extract the samples from the stego file
                        stegoSamplesOne, stegoSamplesTwo, rate = fp.getWaveSamples("Stego2.wav")
                        stegoSamples = np.asarray(stegoSamplesOne, dtype=np.float32, order = 'C') * 32768.0
                  
                        currentTime = time.time()
                        extractMessage, fileType = dwtScale.dwtScaleDecode(list(stegoSamples), LSBs[LSB_index])
                        totalDecodingTime[LSB_index] += time.time() - currentTime
                        extractMessage = AES.decryptBinaryString(extractMessage, AESkeyEncode)

                        
                        if (extractMessage != originalMessage):
                              messageErrors += 1      
                              print(t)
                        
                        
                        # Get the characteristics of the stego file
                        SNR = RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] )
                        capacity = RT.getCapacity(message, samplesUsed, rate)
                        spcc = RT.getSPCC(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed])
                        mse = RT.getMSE(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed])
                        prd = RT.getPRD(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed])
                        psnr = RT.getPSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed])
                              
                        print(counter, end=" ")
                        counter -= 1      
                        
                        
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Alternative'):
                             SNRAlt[LSB_index]    += SNR
                             CapAlt[LSB_index]    += capacity
                             SPCCAlt[LSB_index]   += spcc
                             PRDAlt[LSB_index]    += prd
                             MSEAlt[LSB_index]    += mse
                             PSNRAlt[LSB_index]   += psnr
                             
                             if (SNR < 20):
                                   belowSNR[0][LSB_index] = belowSNR[0][LSB_index] + 1
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Blues'):
                             SNRBlu[LSB_index] += SNR
                             CapBlu[LSB_index] += capacity
                             SPCCBlu[LSB_index]   += spcc
                             PRDBlu[LSB_index]    += prd
                             MSEBlu[LSB_index]    += mse
                             PSNRBlu[LSB_index]   += psnr

                             if (SNR < 20):
                                   belowSNR[1][LSB_index] = belowSNR[1][LSB_index] + 1
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Electronic'):
                             SNREle[LSB_index] += SNR
                             CapEle[LSB_index] += capacity
                             SPCCEle[LSB_index]   += spcc
                             PRDEle[LSB_index]    += prd
                             MSEEle[LSB_index]    += mse
                             PSNREle[LSB_index]   += psnr

                             if (SNR < 20):
                                   belowSNR[2][LSB_index] += 1
                             
                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Jazz'):
                             SNRJzz[LSB_index] += SNR
                             CapJzz[LSB_index] += capacity
                             SPCCJzz[LSB_index]   += spcc
                             PRDJzz[LSB_index]    += prd
                             MSEJzz[LSB_index]    += mse
                             PSNRJzz[LSB_index]   += psnr
                            
                             if (SNR < 20):
                                   belowSNR[3][LSB_index] += 1

                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Pop'):
                             SNRPop[LSB_index] += SNR
                             CapPop[LSB_index] += capacity
                             SPCCPop[LSB_index]   += spcc
                             PRDPop[LSB_index]    += prd
                             MSEPop[LSB_index]    += mse
                             PSNRPop[LSB_index]   += psnr

                             if (SNR < 20):
                                   belowSNR[4][LSB_index] += 1

                        if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Rock'):
                             SNRRoc[LSB_index] += SNR
                             CapRoc[LSB_index] += capacity
                             SPCCRoc[LSB_index]   += spcc
                             PRDRoc[LSB_index]    += prd
                             MSERoc[LSB_index]    += mse
                             PSNRRoc[LSB_index]   += psnr

                             if (SNR < 20):
                                   belowSNR[5][LSB_index] += 1
                       
      
                        
                        
      if (audioOrText == True):
            print("########################################################")
            print("##############   TEXT MESSAGE INFORMATION ##############")
            print("########################################################")
            for LSB_index in range(0, len(LSBs)):
                  plt.figure(13)
                  plt.grid()
                  plt.ylabel('SNR (dB)')
                  plt.plot(x, [SNRAlt[LSB_index]/numSongsPerGenre,SNRBlu[LSB_index]/numSongsPerGenre,SNREle[LSB_index]/numSongsPerGenre,SNRJzz[LSB_index]/numSongsPerGenre,SNRPop[LSB_index]/numSongsPerGenre,SNRRoc[LSB_index]/numSongsPerGenre], label= "LSBs = " + str(LSBs[LSB_index]))
                  plt.legend(loc='best')
                  plt.figure(14)
                  plt.grid()
                  plt.ylabel('Capacity (bits per 16 bit cover sample)')
                  plt.plot(x, [CapAlt[LSB_index]*1000/44100/numSongsPerGenre,CapBlu[LSB_index]*1000/44100/numSongsPerGenre,CapEle[LSB_index]*1000/44100/numSongsPerGenre,CapJzz[LSB_index]*1000/44100/numSongsPerGenre,CapPop[LSB_index]*1000/44100/numSongsPerGenre,CapRoc[LSB_index]*1000/44100/numSongsPerGenre], label= "LSBs = " + str(LSBs[LSB_index]))
                  plt.legend(loc='best')
                  
            print("#################  Statistics for the Scale encoding algorithm     #############")
            for i in range(0, len(LSBs)):
                  print("#########################  LSBs =", LSBs[i], "##########################" )      
                  print("--------  SNR  ")
                  print("# Alterantive",SNRAlt[i]/numSongsPerGenre)
                  print("# Blues      ",SNRBlu[i]/numSongsPerGenre)
                  print("# Electronic ",SNREle[i]/numSongsPerGenre)
                  print("# Jazz       ",SNRJzz[i]/numSongsPerGenre)
                  print("# Pop        ",SNRPop[i]/numSongsPerGenre)
                  print("# Rock       ",SNRRoc[i]/numSongsPerGenre)   
                  print("# Average    ",(SNRAlt[i]/numSongsPerGenre + SNRBlu[i]/numSongsPerGenre + SNREle[i]/numSongsPerGenre + SNRJzz[i]/numSongsPerGenre + SNRPop[i]/numSongsPerGenre + SNRRoc[i]/numSongsPerGenre)/6)      
                  print("--------  PRD  ")
                  print("# Alterantive",PRDAlt[i]/numSongsPerGenre)
                  print("# Blues      ",PRDBlu[i]/numSongsPerGenre)
                  print("# Electronic ",PRDEle[i]/numSongsPerGenre)
                  print("# Jazz       ",PRDJzz[i]/numSongsPerGenre)
                  print("# Pop        ",PRDPop[i]/numSongsPerGenre)
                  print("# Rock       ",PRDRoc[i]/numSongsPerGenre)   
                  print("# Average    ",(PRDAlt[i]/numSongsPerGenre + PRDBlu[i]/numSongsPerGenre + PRDEle[i]/numSongsPerGenre + PRDJzz[i]/numSongsPerGenre + PRDPop[i]/numSongsPerGenre + PRDRoc[i]/numSongsPerGenre)/6)      
                  print("--------  SPCC  ")
                  print("# Alterantive",SPCCAlt[i]/numSongsPerGenre)
                  print("# Blues      ",SPCCBlu[i]/numSongsPerGenre)
                  print("# Electronic ",SPCCEle[i]/numSongsPerGenre)
                  print("# Jazz       ",SPCCJzz[i]/numSongsPerGenre)
                  print("# Pop        ",SPCCPop[i]/numSongsPerGenre)
                  print("# Rock       ",SPCCRoc[i]/numSongsPerGenre)   
                  print("# Average    ",(SPCCAlt[i]/numSongsPerGenre + SPCCBlu[i]/numSongsPerGenre + SPCCEle[i]/numSongsPerGenre + SPCCJzz[i]/numSongsPerGenre + SPCCPop[i]/numSongsPerGenre + SPCCRoc[i]/numSongsPerGenre)/6)      
                  print("--------  MSE  ")
                  print("# Alterantive",MSEAlt[i]/numSongsPerGenre)
                  print("# Blues      ",MSEBlu[i]/numSongsPerGenre)
                  print("# Electronic ",MSEEle[i]/numSongsPerGenre)
                  print("# Jazz       ",MSEJzz[i]/numSongsPerGenre)
                  print("# Pop        ",MSEPop[i]/numSongsPerGenre)
                  print("# Rock       ",MSERoc[i]/numSongsPerGenre)   
                  print("# Average    ",(MSEAlt[i]/numSongsPerGenre + MSEBlu[i]/numSongsPerGenre + MSEEle[i]/numSongsPerGenre + MSEJzz[i]/numSongsPerGenre + MSEPop[i]/numSongsPerGenre + MSERoc[i]/numSongsPerGenre)/6)      
                  print("--------  PSNR  ")
                  print("# Alterantive",PSNRAlt[i]/numSongsPerGenre)
                  print("# Blues      ",PSNRBlu[i]/numSongsPerGenre)
                  print("# Electronic ",PSNREle[i]/numSongsPerGenre)
                  print("# Jazz       ",PSNRJzz[i]/numSongsPerGenre)
                  print("# Pop        ",PSNRPop[i]/numSongsPerGenre)
                  print("# Rock       ",PSNRRoc[i]/numSongsPerGenre)   
                  print("# Average    ",(PSNRAlt[i]/numSongsPerGenre + PSNRBlu[i]/numSongsPerGenre + PSNREle[i]/numSongsPerGenre + PSNRJzz[i]/numSongsPerGenre + PSNRPop[i]/numSongsPerGenre + PSNRRoc[i]/numSongsPerGenre)/6)      
                  print("--------  Capacity  ")
                  print("# Alterantive",CapAlt[i]*1000/44100/numSongsPerGenre)
                  print("# Blues      ",CapBlu[i]*1000/44100/numSongsPerGenre)
                  print("# Electronic ",CapEle[i]*1000/44100/numSongsPerGenre)
                  print("# Jazz       ",CapJzz[i]*1000/44100/numSongsPerGenre)
                  print("# Pop        ",CapPop[i]*1000/44100/numSongsPerGenre)
                  print("# Rock       ",CapRoc[i]*1000/44100/numSongsPerGenre)   
                  print("# Average    ",(CapAlt[i]*1000/44100/numSongsPerGenre + CapBlu[i]*1000/44100/numSongsPerGenre + CapEle[i]*1000/44100/numSongsPerGenre + CapJzz[i]*1000/44100/numSongsPerGenre + CapPop[i]*1000/44100/numSongsPerGenre + CapRoc[i]*1000/44100/numSongsPerGenre)/6)      
                  print("--------  Number of songs below SNR of 20 dB  ")
                  print("# Alterantive",belowSNR[0][i])
                  print("# Blues      ",belowSNR[1][i])
                  print("# Electronic ",belowSNR[2][i])
                  print("# Jazz       ",belowSNR[3][i])
                  print("# Pop        ",belowSNR[4][i])
                  print("# Rock       ",belowSNR[5][i])   
                  print("# Average    ",(belowSNR[0][i]+belowSNR[1][i]+belowSNR[2][i]+belowSNR[3][i]+belowSNR[4][i]+belowSNR[5][i])/6)      
                  print("--------  Average embedding time  ") 
                  print("# Embedding Time    ",totalEncodingTime[i]/(numSongsPerGenre * 6), "seconds")   
            
            print("#################  Statistics for the Scale extraction algorithm     #############")
            print("--------  Number of errors made with extraction", messageErrors) 
                  
            for i in range(0, len(LSBs)):
                        
                  print("# Extraction Time for LSBs = " + str(LSBs[i]),totalDecodingTime[i]/(numSongsPerGenre * 6), "seconds")   
      
      else:
            
            print("########################################################")
            print("##############  AUDIO MESSAGE INFORMATION ##############")
            print("########################################################")
            for LSB_index in range(0, len(LSBs)):
                  plt.figure(15)
                  plt.grid()
                  plt.ylabel('SNR (dB)')
                  plt.plot(x, [SNRAlt[LSB_index]/numSongsPerGenre,SNRBlu[LSB_index]/numSongsPerGenre,SNREle[LSB_index]/numSongsPerGenre,SNRJzz[LSB_index]/numSongsPerGenre,SNRPop[LSB_index]/numSongsPerGenre,SNRRoc[LSB_index]/numSongsPerGenre], label= "LSBs = " + str(LSBs[LSB_index]))
                  plt.legend(loc='best')
                  plt.figure(16)
                  plt.grid()
                  plt.ylabel('Capacity (bits per 16 bit cover sample)')
                  plt.plot(x, [CapAlt[LSB_index]*1000/44100/numSongsPerGenre,CapBlu[LSB_index]*1000/44100/numSongsPerGenre,CapEle[LSB_index]*1000/44100/numSongsPerGenre,CapJzz[LSB_index]*1000/44100/numSongsPerGenre,CapPop[LSB_index]*1000/44100/numSongsPerGenre,CapRoc[LSB_index]*1000/44100/numSongsPerGenre], label= "LSBs = " + str(LSBs[LSB_index]))
                  plt.legend(loc='best')
                  
            print("#################  Statistics for the Scale encoding algorithm     #############")
            for i in range(0, len(LSBs)):
                  print("#########################  LSBs =", LSBs[i], "##########################" )      
                  print("--------  SNR  ")
                  print("# Alterantive",SNRAlt[i]/numSongsPerGenre)
                  print("# Blues      ",SNRBlu[i]/numSongsPerGenre)
                  print("# Electronic ",SNREle[i]/numSongsPerGenre)
                  print("# Jazz       ",SNRJzz[i]/numSongsPerGenre)
                  print("# Pop        ",SNRPop[i]/numSongsPerGenre)
                  print("# Rock       ",SNRRoc[i]/numSongsPerGenre)   
                  print("# Average    ",(SNRAlt[i]/numSongsPerGenre + SNRBlu[i]/numSongsPerGenre + SNREle[i]/numSongsPerGenre + SNRJzz[i]/numSongsPerGenre + SNRPop[i]/numSongsPerGenre + SNRRoc[i]/numSongsPerGenre)/6)      
                  print("--------  PRD  ")
                  print("# Alterantive",PRDAlt[i]/numSongsPerGenre)
                  print("# Blues      ",PRDBlu[i]/numSongsPerGenre)
                  print("# Electronic ",PRDEle[i]/numSongsPerGenre)
                  print("# Jazz       ",PRDJzz[i]/numSongsPerGenre)
                  print("# Pop        ",PRDPop[i]/numSongsPerGenre)
                  print("# Rock       ",PRDRoc[i]/numSongsPerGenre)   
                  print("# Average    ",(PRDAlt[i]/numSongsPerGenre + PRDBlu[i]/numSongsPerGenre + PRDEle[i]/numSongsPerGenre + PRDJzz[i]/numSongsPerGenre + PRDPop[i]/numSongsPerGenre + PRDRoc[i]/numSongsPerGenre)/6)      
                  print("--------  SPCC  ")
                  print("# Alterantive",SPCCAlt[i]/numSongsPerGenre)
                  print("# Blues      ",SPCCBlu[i]/numSongsPerGenre)
                  print("# Electronic ",SPCCEle[i]/numSongsPerGenre)
                  print("# Jazz       ",SPCCJzz[i]/numSongsPerGenre)
                  print("# Pop        ",SPCCPop[i]/numSongsPerGenre)
                  print("# Rock       ",SPCCRoc[i]/numSongsPerGenre)   
                  print("# Average    ",(SPCCAlt[i]/numSongsPerGenre + SPCCBlu[i]/numSongsPerGenre + SPCCEle[i]/numSongsPerGenre + SPCCJzz[i]/numSongsPerGenre + SPCCPop[i]/numSongsPerGenre + SPCCRoc[i]/numSongsPerGenre)/6)      
                  print("--------  MSE  ")
                  print("# Alterantive",MSEAlt[i]/numSongsPerGenre)
                  print("# Blues      ",MSEBlu[i]/numSongsPerGenre)
                  print("# Electronic ",MSEEle[i]/numSongsPerGenre)
                  print("# Jazz       ",MSEJzz[i]/numSongsPerGenre)
                  print("# Pop        ",MSEPop[i]/numSongsPerGenre)
                  print("# Rock       ",MSERoc[i]/numSongsPerGenre)   
                  print("# Average    ",(MSEAlt[i]/numSongsPerGenre + MSEBlu[i]/numSongsPerGenre + MSEEle[i]/numSongsPerGenre + MSEJzz[i]/numSongsPerGenre + MSEPop[i]/numSongsPerGenre + MSERoc[i]/numSongsPerGenre)/6)      
                  print("--------  PSNR  ")
                  print("# Alterantive",PSNRAlt[i]/numSongsPerGenre)
                  print("# Blues      ",PSNRBlu[i]/numSongsPerGenre)
                  print("# Electronic ",PSNREle[i]/numSongsPerGenre)
                  print("# Jazz       ",PSNRJzz[i]/numSongsPerGenre)
                  print("# Pop        ",PSNRPop[i]/numSongsPerGenre)
                  print("# Rock       ",PSNRRoc[i]/numSongsPerGenre)   
                  print("# Average    ",(PSNRAlt[i]/numSongsPerGenre + PSNRBlu[i]/numSongsPerGenre + PSNREle[i]/numSongsPerGenre + PSNRJzz[i]/numSongsPerGenre + PSNRPop[i]/numSongsPerGenre + PSNRRoc[i]/numSongsPerGenre)/6)      
                  print("--------  Capacity  ")
                  print("# Alterantive",CapAlt[i]*1000/44100/numSongsPerGenre)
                  print("# Blues      ",CapBlu[i]*1000/44100/numSongsPerGenre)
                  print("# Electronic ",CapEle[i]*1000/44100/numSongsPerGenre)
                  print("# Jazz       ",CapJzz[i]*1000/44100/numSongsPerGenre)
                  print("# Pop        ",CapPop[i]*1000/44100/numSongsPerGenre)
                  print("# Rock       ",CapRoc[i]*1000/44100/numSongsPerGenre)   
                  print("# Average    ",(CapAlt[i]*1000/44100/numSongsPerGenre + CapBlu[i]*1000/44100/numSongsPerGenre + CapEle[i]*1000/44100/numSongsPerGenre + CapJzz[i]*1000/44100/numSongsPerGenre + CapPop[i]*1000/44100/numSongsPerGenre + CapRoc[i]*1000/44100/numSongsPerGenre)/6)      
                  print("--------  Number of songs below SNR of 20 dB  ")
                  print("# Alterantive",belowSNR[0][i])
                  print("# Blues      ",belowSNR[1][i])
                  print("# Electronic ",belowSNR[2][i])
                  print("# Jazz       ",belowSNR[3][i])
                  print("# Pop        ",belowSNR[4][i])
                  print("# Rock       ",belowSNR[5][i])   
                  print("# Average    ",(belowSNR[0][i]+belowSNR[1][i]+belowSNR[2][i]+belowSNR[3][i]+belowSNR[4][i]+belowSNR[5][i])/6)      
                  print("--------  Average embedding time  ") 
                  print("# Embedding Time    ",totalEncodingTime[i]/(numSongsPerGenre * 6), "seconds")   
            
            print("#################  Statistics for the Scale extraction algorithm     #############")
            print("--------  Number of errors made with extraction", messageErrors) 
                  
            for i in range(0, len(LSBs)):
                        
                  print("# Extraction Time for LSBs = " + str(LSBs[i]),totalDecodingTime[i]/(numSongsPerGenre * 6), "seconds")   

