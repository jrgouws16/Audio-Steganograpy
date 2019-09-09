# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 15:04:23 2019

@author: Johan Gouws
"""

import ResultsAndTesting as RT
import geneticAlgorithm as GA
import LSB
import dwtFirstPrinciples as dwtFP
import dwtLibrary as dwtL
import os
import wave
import fileprocessing as fp
import random
from copy import deepcopy
import time

doSingleTest = True
doSongDataBase = True

if doSongDataBase == True:

    
    path = 'Media/SongDatabase'
    #path = 
    
    coverFiles = []
    messageFiles = []
    
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if '.wav' in file:
                coverFiles.append(os.path.join(r, file))
    
    print("################# Standard LSB encoding  #############################")
    for i in coverFiles:
        stegoSamples = []
        
        # Get the stego file name to be saved to from the line edit box
        stegoFileName = 'Media/stego.wav'
        
        # Open the cover audio file
        song = wave.open(i, mode='rb')
        
        # Extract the cover samples
        coverSamples = fp.extractWaveSamples(song)
        originalCoverSamples = deepcopy(coverSamples[0])
        
        # Read the secret message file
        secretMessage = [random.randrange(0, 2) for i in range(len(coverSamples[0]))]
    
        print("Cover file =", i)
        
        for j in range(1, 8):
              print('##############  LSB embedding, with LSB =', j, "############")
              print("Bits encoded =", len(secretMessage))
              
              start_time = time.time()
              
    
              
              # Provide first audio channel samples and message samples to encode 
              LSB_encoding = LSB.LSB_encoding(coverSamples[0], secretMessage)
              
              # Embed the message
              LSB_encoding.encode(j)
              print((time.time() - start_time), "seconds to execute embedding algorithm")         
              stegoSamples = LSB_encoding.stegoSamples
              samplesUsed = LSB_encoding.numberSamplesUsed
              print("Samples used:", samplesUsed)
              print("SNR =", RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed]))
              print("Capacity of " + str(RT.getCapacity(secretMessage, samplesUsed, song.getframerate())) + " kbps.")
              
        print("")  
        song.close()
    
    
    print("################# Genetic algorithm encoding  ########################")
    for i in coverFiles:
        stegoSamples = []
        
        # Get the stego file name to be saved to from the line edit box
        stegoFileName = 'Media/stego.wav'
        
        # Open the cover audio file
        song = wave.open(i, mode='rb')
        
        # Extract the cover samples
        coverSamples = fp.extractWaveSamples(song)
            
        # Read the secret message file
        secretMessage = [random.randrange(0, 2) for i in range(len(coverSamples[0]))]
    
        print("Cover file =", i)            
        # Second method = Genetic Algorithm
        # Get the string representation of the key in ASCII
        keyString = "GA_testing"
            
        # Convert ASCII to binary 
        binaryKey = fp.messageToBinary(keyString) 
        binaryKey = binaryKey * int((len(secretMessage) + float(len(secretMessage))/len(binaryKey)) )
        
        
        originalCoverSamples = deepcopy(coverSamples[0])
          
        for i in range(0, len(coverSamples[0])):
             coverSamples[0][i] = "{0:016b}".format(coverSamples[0][i])
          
        secretMessage = "".join(map(str,secretMessage))
          
        # Provide first audio channel samples and message samples to encode 
        start_time = time.time()
        stegoSamples, samplesUsed, bitsInserted = GA.insertMessage(coverSamples[0], binaryKey, "".join(map(str, secretMessage)), "txt")
        print((time.time() - start_time), "seconds to execute embedding algorithm")          
        # Convert the binary audio samples to decimal samples
        for i in range(0, len(stegoSamples)):
            stegoSamples[i] = int(stegoSamples[i], 2)
          
        # Get the characteristics of the stego file
        print("Embedded " + str(bitsInserted) + " bits into " + str(samplesUsed) + " samples.")
        print("SNR of " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] ), 2)))
        print("Capacity of " + str(RT.getCapacity(secretMessage, samplesUsed, song.getframerate())) + " kbps.")
            
        print("")  
        song.close()
        
        
    print("################# DWT Haar embedding library    ######################")
    for i in coverFiles:
        for j in range(0,6):  
              print("###################  OBH =", j, "###########################")
              
              stegoSamples = []
              
              # Get the stego file name to be saved to from the line edit box
              stegoFileName = 'Media/stego.wav'
              
              # Open the cover audio file
              song = wave.open(i, mode='rb')
              
              # Extract the cover samples
              coverSamples = fp.extractWaveSamples(song)
                  
              # Read the secret message file
              secretMessage = [random.randrange(0, 2) for i in range(len(coverSamples[0]))]
          
              print("Cover file =", i)            
              
              originalCoverSamples = deepcopy(coverSamples[0])
              
              secretMessage = "".join(map(str,secretMessage))
              
              
              start_time = time.time()
              stegoSamples, samplesUsed = dwtL.dwtHaarEncodingLibrary(coverSamples[0], secretMessage, j, 2048)
              print((time.time() - start_time), "seconds to execute embedding algorithm")               
              # Get the characteristics of the stego file
              print("Embedded " + str(bitsInserted) + " bits into " + str(samplesUsed) + " samples.")
              print("SNR of " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] ), 2)))
              print("Capacity of " + str(RT.getCapacity(secretMessage, samplesUsed, song.getframerate())) + " kbps.")
                  
              print("")  
              song.close()    
            
    print("################# DWT Haar embedding first principles  ###############")
    for i in coverFiles:
          for j in range(0,6):  
              print("###################  OBH =", j, "###########################")
        
              stegoSamples = []
              
              # Get the stego file name to be saved to from the line edit box
              stegoFileName = 'Media/stego.wav'
              
              # Open the cover audio file
              song = wave.open(i, mode='rb')
              
              # Extract the cover samples
              coverSamples = fp.extractWaveSamples(song)
                  
              # Read the secret message file
              secretMessage = [random.randrange(0, 2) for i in range(len(coverSamples[0]))]
          
              print("Cover file =", i)            
              
              originalCoverSamples = deepcopy(coverSamples[0])
              
              secretMessage = "".join(map(str,secretMessage))
              start_time = time.time()
              stegoSamples, samplesUsed = dwtFP.dwtHaarEncode(coverSamples[0], secretMessage, j, 2048, "txt")
              print((time.time() - start_time), "seconds to execute embedding algorithm")         
                
              # Get the characteristics of the stego file
              print("Embedded " + str(bitsInserted) + " bits into " + str(samplesUsed) + " samples.")
              print("SNR of " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] ), 2)))
              print("Capacity of " + str(RT.getCapacity(secretMessage, samplesUsed, song.getframerate())) + " kbps.")
                  
              print("")  
              song.close()        
              
              
if doSingleTest == True:
      print("################# DWT haar algorithm encoding  #######################")

      stegoSamples = []
      
      # Get the stego file name to be saved to from the line edit box
      stegoFileName = 'Media/stego.wav'
      
      # Open the cover audio file
      song = wave.open("Media/opera.wav", mode='rb')
      
      # Extract the cover samples
      coverSamples = fp.extractWaveSamples(song)
          
      # Read the secret message file
      secretMessage = [random.randrange(0, 2) for i in range(int(len(coverSamples[0])/11))]
       
      originalCoverSamples = deepcopy(coverSamples[0])
      
      secretMessage = "".join(map(str,secretMessage))
      start_time = time.time()
      stegoSamples, samplesUsed = dwtFP.dwtHaarEncode(coverSamples[0], secretMessage, 1, 1024, "txt")
      print((time.time() - start_time), "seconds to execute embedding algorithm")         
        
      # Get the characteristics of the stego file
      print("Embedded " + str(len(secretMessage)) + " bits into " + str(samplesUsed) + " samples.")
      print("SNR of " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] ), 2)))
      print("Capacity of " + str(RT.getCapacity(secretMessage, samplesUsed, song.getframerate())) + " kbps.")
          
      print("")  
      song.close()      
      
      
      print("################# Genetic algorithm encoding  ########################")
      stegoSamples = []
        
      # Get the stego file name to be saved to from the line edit box
      stegoFileName = 'Media/stego.wav'
        
      # Open the cover audio file
      song = wave.open("Media/opera.wav", mode='rb')
        
      # Extract the cover samples
      coverSamples = fp.extractWaveSamples(song)
            
      # Read the secret message file
      secretMessage = [random.randrange(0, 2) for i in range(len(coverSamples[0]))]
      print(len(secretMessage))
      
      # Second method = Genetic Algorithm
      # Get the string representation of the key in ASCII
      keyString = "llllll"
            
      # Convert ASCII to binary 
      binaryKey = fp.messageToBinary(keyString) 
      binaryKey = binaryKey * int((len(secretMessage) + float(len(secretMessage))/len(binaryKey)) )
        
        
      originalCoverSamples = deepcopy(coverSamples[0])
          
      for i in range(0, len(coverSamples[0])):
           coverSamples[0][i] = "{0:016b}".format(coverSamples[0][i])
          
      secretMessage = "".join(map(str,secretMessage))
          
      # Provide first audio channel samples and message samples to encode 
      start_time = time.time()
      stegoSamples, samplesUsed, bitsInserted = GA.insertMessage(coverSamples[0], binaryKey, "".join(map(str, secretMessage)), "txt")
      print((time.time() - start_time), "seconds to execute embedding algorithm")          
      # Convert the binary audio samples to decimal samples
      for i in range(0, len(stegoSamples)):
          stegoSamples[i] = int(stegoSamples[i], 2)
          
      # Get the characteristics of the stego file
      print("Embedded " + str(bitsInserted) + " bits into " + str(samplesUsed) + " samples.")
      print("SNR of " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] ), 2)))
      print("Capacity of " + str(RT.getCapacity(secretMessage, samplesUsed, song.getframerate())) + " kbps.")
            
      print("")  
      song.close()
        
        
        
        
        
        
        
    