import ResultsAndTesting as RT
import dwtHybrid
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
textMessage = True

x = ['Alternative','Blues','Electronic','Jazz','Pop','Rock']
x = np.asarray(x)

OBHs = [8,9,10]

for audioOrText in [True]:

      
      counter = numSongsPerGenre * 6 * len(OBHs)
      
      SNRAlt = [0]*len(OBHs)
      SNRBlu = [0]*len(OBHs)
      SNREle = [0]*len(OBHs)
      SNRJzz = [0]*len(OBHs)
      SNRPop = [0]*len(OBHs)
      SNRRoc = [0]*len(OBHs)
      
      CapAlt = [0]*len(OBHs)
      CapBlu = [0]*len(OBHs)
      CapEle = [0]*len(OBHs)
      CapJzz = [0]*len(OBHs)
      CapPop = [0]*len(OBHs)
      CapRoc = [0]*len(OBHs)
      
      PRDAlt = [0]*len(OBHs)
      PRDBlu = [0]*len(OBHs)
      PRDEle = [0]*len(OBHs)
      PRDJzz = [0]*len(OBHs)
      PRDPop = [0]*len(OBHs)
      PRDRoc = [0]*len(OBHs)
      
      SPCCAlt = [0]*len(OBHs)
      SPCCBlu = [0]*len(OBHs)
      SPCCEle = [0]*len(OBHs)
      SPCCJzz = [0]*len(OBHs)
      SPCCPop = [0]*len(OBHs)
      SPCCRoc = [0]*len(OBHs)
      
      MSEAlt = [0]*len(OBHs)
      MSEBlu = [0]*len(OBHs)
      MSEEle = [0]*len(OBHs)
      MSEJzz = [0]*len(OBHs)
      MSEPop = [0]*len(OBHs)
      MSERoc = [0]*len(OBHs)
      
      PSNRAlt = [0]*len(OBHs)
      PSNRBlu = [0]*len(OBHs)
      PSNREle = [0]*len(OBHs)
      PSNRJzz = [0]*len(OBHs)
      PSNRPop = [0]*len(OBHs)
      PSNRRoc = [0]*len(OBHs)
      
      belowSNR = []
      
      for i in range(6):
            belowSNR.append([0]*len(OBHs))
      
      totalEncodingTime = [0]*len(OBHs)
      totalDecodingTime = [0]*len(OBHs)
      
      
      messageErrors = []
      for i in range(0,6):
            messageErrors.append([0]*len(OBHs))
      
      
      for path in allPaths:
            coverFiles = []
                
            for r, d, f in os.walk(path):
              for file in f:
                  if '.wav' in file:
                      coverFiles.append(os.path.join(r, file))
      
      
            coverFiles = coverFiles[0:numSongsPerGenre]
            if (textMessage == True):
                  
                  for t in coverFiles:
                        for OBH_index in range(0,len(OBHs)):
                              AESkeyEncode = "THIS_IS_THE_KEY_USED_FOR_AES_ENCRYPTION"
                          
                              samplesOne, samplesTwo, rate = fp.getWaveSamples(t)
                          
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
                      
                              originalCoverSamples = deepcopy(samplesOne)
                        
                              currentTime = time.time()
                              stegoSamples, samplesUsed, capacityWarning = dwtHybrid.dwtHybridEncode(samplesOne, message, '.txt', OBHs[OBH_index])
                              totalEncodingTime[OBH_index] += time.time() - currentTime                    
      
      
                              if (capacityWarning == True):
                                    print("Whoah the capacity is too small of the cover file")
      
                              stegoSamples = np.asarray(stegoSamples, dtype=np.float32, order = 'C')/32768.0
                              scWave.write("Stego5.wav", rate, stegoSamples)
                          
                              # Open the steganography file
                              samplesOneStego, samplesTwoStego, rate = fp.getWaveSamples("Stego5.wav")
                              samplesOneStego = np.asarray(samplesOneStego, dtype=np.float32, order = 'C')*32768.0
                                
                              # Extract the wave samples from the host signal
                              currentTime = time.time()
                              extractMessage, fileType = dwtHybrid.dwtHybridDecode(samplesOneStego, OBHs[OBH_index])
                              totalDecodingTime[OBH_index] += time.time() - currentTime
      
      
                              extractMessage = AES.decryptBinaryString(extractMessage, "THIS_IS_THE_KEY_USED_FOR_AES_ENCRYPTION")
                         
                              # Get the characteristics of the stego file
                              SNR = RT.getSNR(originalCoverSamples[0:samplesUsed], samplesOneStego[0:samplesUsed] )
                              capacity = RT.getCapacity(message, samplesUsed, rate)
                              spcc = RT.getSPCC(originalCoverSamples[0:samplesUsed], samplesOneStego[0:samplesUsed])
                              mse = RT.getMSE(originalCoverSamples[0:samplesUsed], samplesOneStego[0:samplesUsed])
                              prd = RT.getPRD(originalCoverSamples[0:samplesUsed], samplesOneStego[0:samplesUsed])
                              psnr = RT.getPSNR(originalCoverSamples[0:samplesUsed], samplesOneStego[0:samplesUsed])
                              
                              print(counter, end=" ")
                              counter -= 1      
                              
                              
                              if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Alternative'):
                                   SNRAlt[OBH_index]    += SNR
                                   CapAlt[OBH_index]    += capacity
                                   SPCCAlt[OBH_index]   += spcc
                                   PRDAlt[OBH_index]    += prd
                                   MSEAlt[OBH_index]    += mse
                                   PSNRAlt[OBH_index]   += psnr
                              
                                   if (extractMessage != originalMessage):
                                          messageErrors[0][OBH_index] += 1      
                                          print(t)
                              
                                   if (SNR < 20):
                                         belowSNR[0][OBH_index] = belowSNR[0][OBH_index] + 1
                                   
                              if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Blues'):
                                   SNRBlu[OBH_index] += SNR
                                   CapBlu[OBH_index] += capacity
                                   SPCCBlu[OBH_index]   += spcc
                                   PRDBlu[OBH_index]    += prd
                                   MSEBlu[OBH_index]    += mse
                                   PSNRBlu[OBH_index]   += psnr
      
                                   if (extractMessage != originalMessage):
                                          messageErrors[1][OBH_index] += 1      
                                          print(t)
      
                                   if (SNR < 20):
                                         belowSNR[1][OBH_index] = belowSNR[1][OBH_index] + 1
                                   
                              if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Electronic'):
                                   SNREle[OBH_index] += SNR
                                   CapEle[OBH_index] += capacity
                                   SPCCEle[OBH_index]   += spcc
                                   PRDEle[OBH_index]    += prd
                                   MSEEle[OBH_index]    += mse
                                   PSNREle[OBH_index]   += psnr
                                   
                                   if (extractMessage != originalMessage):
                                          messageErrors[2][OBH_index] += 1      
                                          print(t)
                                   
                                   if (SNR < 20):
                                         belowSNR[2][OBH_index] += 1
                                   
                              if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Jazz'):
                                   SNRJzz[OBH_index] += SNR
                                   CapJzz[OBH_index] += capacity
                                   SPCCJzz[OBH_index]   += spcc
                                   PRDJzz[OBH_index]    += prd
                                   MSEJzz[OBH_index]    += mse
                                   PSNRJzz[OBH_index]   += psnr
                                  
                                   if (extractMessage != originalMessage):
                                          messageErrors[3][OBH_index] += 1      
                                          print(t) 
                                   
                                   if (SNR < 20):
                                         belowSNR[3][OBH_index] += 1
      
                              if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Pop'):
                                   SNRPop[OBH_index] += SNR
                                   CapPop[OBH_index] += capacity
                                   SPCCPop[OBH_index]   += spcc
                                   PRDPop[OBH_index]    += prd
                                   MSEPop[OBH_index]    += mse
                                   PSNRPop[OBH_index]   += psnr
      
                                   if (extractMessage != originalMessage):
                                          messageErrors[4][OBH_index] += 1      
                                          print(t)
      
                                   if (SNR < 20):
                                         belowSNR[4][OBH_index] += 1
      
                              if (path == 'C:/Users/Johan Gouws/Desktop/GenresDatabase/Rock'):
                                   SNRRoc[OBH_index] += SNR
                                   CapRoc[OBH_index] += capacity
                                   SPCCRoc[OBH_index]   += spcc
                                   PRDRoc[OBH_index]    += prd
                                   MSERoc[OBH_index]    += mse
                                   PSNRRoc[OBH_index]   += psnr
      
                                   if (extractMessage != originalMessage):
                                          messageErrors[5][OBH_index] += 1      
                                          print(t)
      
                                   if (SNR < 20):
                                         belowSNR[5][OBH_index] += 1
      
      if (audioOrText == True):
            print("########################################################")
            print("##############   TEXT MESSAGE INFORMATION ##############")
            print("########################################################")
            for OBH_index in range(0, len(OBHs)):
                  plt.figure(21)
                  plt.grid()
                  plt.ylabel('SNR (dB)')
                  plt.plot(x, [SNRAlt[OBH_index]/numSongsPerGenre,SNRBlu[OBH_index]/numSongsPerGenre,SNREle[OBH_index]/numSongsPerGenre,SNRJzz[OBH_index]/numSongsPerGenre,SNRPop[OBH_index]/numSongsPerGenre,SNRRoc[OBH_index]/numSongsPerGenre], label= "OBHs = " + str(OBHs[OBH_index]))
                  plt.legend(loc='upper right')
                  plt.figure(22)
                  plt.grid()
                  plt.ylabel('Capacity (bits per 16 bit cover sample)')
                  plt.plot(x, [CapAlt[OBH_index]*1000/44100/numSongsPerGenre,CapBlu[OBH_index]*1000/44100/numSongsPerGenre,CapEle[OBH_index]*1000/44100/numSongsPerGenre,CapJzz[OBH_index]*1000/44100/numSongsPerGenre,CapPop[OBH_index]*1000/44100/numSongsPerGenre,CapRoc[OBH_index]*1000/44100/numSongsPerGenre], label= "OBHs = " + str(OBHs[OBH_index]))
                  plt.legend(loc='upper right')
                  
            print("#################  Statistics for the Hybrid encoding algorithm     #############")
            for i in range(0, len(OBHs)):
                  print("#########################  OBHs =", OBHs[i], "##########################" )      
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
            
            print("#################  Statistics for the Hybrid extraction algorithm     #############")
            print("--------  Number of errors made with extraction") 
            
            for i in range(0, len(OBHs)):
                  print('OBH =', str(OBHs[i]))
                  print("# Alterantive",messageErrors[0][i])
                  print("# Blues      ",messageErrors[1][i])
                  print("# Electronic ",messageErrors[2][i])
                  print("# Jazz       ",messageErrors[3][i])
                  print("# Pop        ",messageErrors[4][i])
                  print("# Rock       ",messageErrors[5][i]) 
                  
            for i in range(0, len(OBHs)):
                        
                  print("# Extraction Time for OBHs = " + str(OBHs[i]),totalDecodingTime[i]/(numSongsPerGenre * 6), "seconds")   
      
      else:
            print("########################################################")
            print("##############   AUDIO MESSAGE INFORMATION ##############")
            print("########################################################")
            for OBH_index in range(0, len(OBHs)):
                  plt.figure(23)
                  plt.grid()
                  plt.ylabel('SNR (dB)')
                  plt.plot(x, [SNRAlt[OBH_index]/numSongsPerGenre,SNRBlu[OBH_index]/numSongsPerGenre,SNREle[OBH_index]/numSongsPerGenre,SNRJzz[OBH_index]/numSongsPerGenre,SNRPop[OBH_index]/numSongsPerGenre,SNRRoc[OBH_index]/numSongsPerGenre], label= "OBHs = " + str(OBHs[OBH_index]))
                  plt.legend(loc='upper right')
                  plt.figure(24)
                  plt.grid()
                  plt.ylabel('Capacity (bits per 16 bit cover sample)')
                  plt.plot(x, [CapAlt[OBH_index]*1000/44100/numSongsPerGenre,CapBlu[OBH_index]*1000/44100/numSongsPerGenre,CapEle[OBH_index]*1000/44100/numSongsPerGenre,CapJzz[OBH_index]*1000/44100/numSongsPerGenre,CapPop[OBH_index]*1000/44100/numSongsPerGenre,CapRoc[OBH_index]*1000/44100/numSongsPerGenre], label= "OBHs = " + str(OBHs[OBH_index]))
                  plt.legend(loc='upper right')
                  
            print("#################  Statistics for the Hybrid encoding algorithm     #############")
            for i in range(0, len(OBHs)):
                  print("#########################  OBHs =", OBHs[i], "##########################" )      
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
            
            print("#################  Statistics for the Hybrid extraction algorithm     #############")
            print("--------  Number of errors made with extraction")
            for i in range(0, len(OBHs)):
                  print('OBH =', str(OBHs[i]))
                  print("# Alterantive",messageErrors[0][i])
                  print("# Blues      ",messageErrors[1][i])
                  print("# Electronic ",messageErrors[2][i])
                  print("# Jazz       ",messageErrors[3][i])
                  print("# Pop        ",messageErrors[4][i])
                  print("# Rock       ",messageErrors[5][i]) 
                  
            for i in range(0, len(OBHs)):
                        
                  print("# Extraction Time for OBHs = " + str(OBHs[i]),totalDecodingTime[i]/(numSongsPerGenre * 6), "seconds")   
