# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 20:47:42 2019

@author: Johan Gouws
"""
from PyQt5 import QtWidgets, uic
from copy import deepcopy
import socket
import threading
import sys
import fileprocessing as fp
import sockets
import geneticAlgorithm as GA
import dwtOBH
import dwtScale
import dwtHybrid
import dwtEncrypt as DWTcrypt
import ResultsAndTesting as RT
import os
import time
import scipy.io.wavfile as scWave
import numpy as np
import AES
import SignalsAndSlots as SS

wrongUnamePword = SS.showErrorSigSlot()
wrongUnamePword.title = "Wrong username and password"
wrongUnamePword.info = "Enter the correct username and password combination and try again."
rightUnamePword = SS.showInfoSigSlot()
rightUnamePword.title = "Correct username and password"
rightUnamePword.info = "Server accessed successfully."
changeUnamePword = SS.showInfoSigSlot()
changeUnamePword.title = "Change successful"
changeUnamePword.info = "Username and password changed successfully."

serverThread = []
connections  = []
addresses    = []
attemptsLeft = []

clientsConnected = 0
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Function for encoding using the standard LSB encoding algorithm
def GA_encoding(coverSamples, secretMessage, key, frameRate, fileType):
        # Deepcopy for calculating the SNR
        originalCoverSamples = deepcopy(coverSamples[0])

        for i in range(0, len(coverSamples[0])):
            coverSamples[0][i] = "{0:016b}".format(coverSamples[0][i])

        secretMessage = "".join(map(str,secretMessage))
    
        # Provide first audio channel samples and message samples to encode 
        stegoSamples, samplesUsed, bitsInserted, capacityWarning = GA.insertMessage(coverSamples[0], key, "".join(map(str, secretMessage)), fileType)
        
        # Convert the binary audio samples to decimal samples
        for i in range(0, len(stegoSamples)):
            stegoSamples[i] = int(stegoSamples[i], 2)
        
            if (stegoSamples[i] < -32768):
                stegoSamples[i] = -32768
            
            if (stegoSamples[i] > 32767):
                stegoSamples[i] = 32767
        
        # Get the characteristics of the stego file
        infoMessage = "Embedded " + str(round(bitsInserted/samplesUsed, 5)) + " bits per sample on average."
        infoMessage += "\nSNR of " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] ), 2))
        infoMessage += ".\nCapacity of " + str(RT.getCapacity(secretMessage, samplesUsed, frameRate)) + " kbps."       
        # Show the results of the stego quality of the stego file
        mainWindow.listWidget_log.addItem(infoMessage)
                
        return stegoSamples, capacityWarning, infoMessage
    
# Function to extract the message from the stego file making use of 
# Genetic Algorithm
def GA_decoding(stegoSamples, key):
    
    # Convert integer samples to binary samples
    for i in range(0, len(stegoSamples)):
                
        stegoSamples[i] = "{0:016b}".format(int(stegoSamples[i]))
        
    # Extract secret message
    secretMessage, fileType = GA.extractMessage(stegoSamples, key)
        
    return secretMessage, fileType
   

def threaded_client(conn, clientNum):
    global clientsConnected
    mainWindow.listWidget_log.addItem("Client thread created successfully")  
    fileType = ''
    authenticated = False
    
    
    while True:
#        try:
            message = sockets.recv_one_message(conn)
            print(message)   
            if (message == None):
                  break
            
            elif (message.decode() == "Authenticate"):
                  username = sockets.recv_one_message(conn).decode()
                  password = sockets.recv_one_message(conn).decode()
                  
                  compUsernameObj = open('UnamePword/username.txt', 'r')
                  compPasswordObj = open('UnamePword/password.txt', 'r')
                  
                  compUsername = compUsernameObj.read()
                  compPassword = compPasswordObj.read()
                  
                  if (compUsername == username and compPassword == password):
                        authenticated = True
                        sockets.send_one_message(conn, "Authenticated")
                        
                  else:
                        sockets.send_one_message(conn, "Not_authenticated")
                        sockets.send_one_message(conn, "1")

            
            elif (message.decode() == "Capacity" and authenticated == True):
                cover = open(str(clientNum) + "Capacity" + ".wav", "wb")
                data = sockets.recv_one_message(conn)
                cover.write(data)
                cover.close()
                
                method = sockets.recv_one_message(conn)
                
                if (method.decode() == "DWT"):
                    OBH = sockets.recv_one_message(conn)
                    OBH = int(OBH.decode())
                    samplesOne, samplesTwo, rate = fp.getWaveSamples(str(clientNum) + "Capacity" + ".wav")
                    capacity = dwtOBH.getCapacity(samplesOne, OBH, 512)
                    sockets.send_one_message(conn, "Capacity")
                    sockets.send_one_message(conn, str(capacity))
                    
                elif (method.decode() == "DWT_hybrid"):
                    OBH = sockets.recv_one_message(conn)
                    OBH = int(OBH.decode())
                    samplesOne, samplesTwo, rate = fp.getWaveSamples(str(clientNum) + "Capacity" + ".wav")
                    capacity = dwtHybrid.getCapacity(samplesOne, OBH)
                    sockets.send_one_message(conn, "Capacity")
                    sockets.send_one_message(conn, str(capacity))
                    
                elif (method.decode() == "DWT_scale"):
                    LSBs = sockets.recv_one_message(conn)
                    LSBs = int(LSBs.decode())
                    samplesOne, samplesTwo, rate = fp.getWaveSamples(str(clientNum) + "Capacity" + ".wav")
                    capacity = dwtScale.getCapacity(samplesOne, LSBs)
                    sockets.send_one_message(conn, "Capacity")
                    sockets.send_one_message(conn, str(capacity))
                    
                elif (method.decode() == "DWT_encode"):
                    samplesOne, samplesTwo, rate = fp.getWaveSamples(str(clientNum) + "Capacity" + ".wav")
                    capacity = DWTcrypt.getCapacity(samplesOne, 512)
                    sockets.send_one_message(conn, "Capacity")
                    sockets.send_one_message(conn, str(capacity))
                    
                elif (method.decode() == "GA"):
                    samplesOne, samplesTwo, rate = fp.getWaveSamples(str(clientNum) + "Capacity" + ".wav")
                    sockets.send_one_message(conn, "Capacity")
                    sockets.send_one_message(conn, str(len(samplesOne)*1.5))
              
            # If it is needed to encode the message into the audio    
            elif (message.decode() == "Encode" and authenticated == True):
                
                mainWindow.listWidget_log.addItem("Client " + str(addresses[connections.index(conn)][0]) + " requested encoding.")
                
                # Receive the audio cover file
                mainWindow.listWidget_log.addItem("Incoming cover: " + str(addresses[connections.index(conn)][0]) )
                song = open(str(clientNum) + ".wav", "wb")
                data = sockets.recv_one_message(conn)
                song.write(data)
                song.close()
                mainWindow.listWidget_log.addItem("Cover received: " + str(addresses[connections.index(conn)][0]) )
                
                # Receive the message file
                fileType = sockets.recv_one_message(conn)
                fileType = fileType.decode()
                                
                mainWindow.listWidget_log.addItem("Incomming message: " + str(addresses[connections.index(conn)][0]))
                
                if (fileType == ".wav"):
                    secretMessageObj = open(str(clientNum) + "MSG" + ".wav", "wb")
                    data = sockets.recv_one_message(conn)
                    secretMessageObj.write(data)
                    secretMessageObj.close()
                    mainWindow.listWidget_log.addItem("Message received: " + str(addresses[connections.index(conn)][0]))
                    
                elif (fileType == ".txt"):
                    secretMessageObj = open(str(clientNum) + "MSG" + ".txt", "wb")
                    data = sockets.recv_one_message(conn)
                    secretMessageObj.write(data)
                    secretMessageObj.close()
                    mainWindow.listWidget_log.addItem("Message received: " + str(addresses[connections.index(conn)][0]))    
                
                AESkeyEncode = sockets.recv_one_message(conn).decode()
                mainWindow.listWidget_log.addItem("AES key received - " + AESkeyEncode + ": " + str(addresses[connections.index(conn)][0]))
                
                # Receive the encoding method
                method = sockets.recv_one_message(conn)
                
                mainWindow.listWidget_log.addItem("Encoding mode selected - " + method.decode() + ": " + str(addresses[connections.index(conn)][0]))
                
                
                if (method.decode() == "GA"):
                    stegoSamples = []
        
                    # Get the string representation of the key in ASCII
                    keyString = sockets.recv_one_message(conn)
                    mainWindow.listWidget_log.addItem("Key: " + keyString.decode() + ": " + str(addresses[connections.index(conn)][0]))
                    
                    # Receive the recipients to whom to send to
                    # CP = Client and Peer
                    # P  = Peer
                    # C  = Client
                    toWhom = sockets.recv_one_message(conn)
                    toWhom = toWhom.decode()
                                    
                    # Extract the cover samples from the cover audio file
                    mainWindow.listWidget_log.addItem("Embedding stego: "+ str(addresses[connections.index(conn)][0]))
                    coverSamplesOne, coverSamplesTwo, rate = fp.getWaveSamples(str(clientNum) + ".wav")
                    
                    for i in range(0, len(coverSamplesOne)):
                        if (coverSamplesOne[i] <= -32768):       
                                coverSamplesOne[i] += 1
                    
                    coverSamples = [coverSamplesOne, coverSamplesTwo]

                    secretMessage = ""
                    if (fileType == ".wav"):
     
                        # Get the audio samples in integer form converted to binary
                        intSamples = fp.extractWaveMessage(str(clientNum) + "MSG" + fileType)
    
                        # Convert to integer list of bits for embedding
                        secretMessage = "".join(intSamples[0])
                        
                        # Encrypt the secret message
                        mainWindow.listWidget_log.addItem("AES encryption Starting: "+ str(addresses[connections.index(conn)][0]))
                        secretMessage = AES.encryptBinaryString(secretMessage, AESkeyEncode)
                        mainWindow.listWidget_log.addItem("AES encryption completed: "+ str(addresses[connections.index(conn)][0]))
    
                        secretMessage = list(map(int, list(secretMessage)))
                    
                    else:
                        secretMessage = fp.getMessageBits(str(clientNum) + "MSG" + fileType)
                        secretMessage = list(map(str, secretMessage))
                        secretMessage = ''.join(secretMessage)
                        mainWindow.listWidget_log.addItem("AES encryption Starting: "+ str(addresses[connections.index(conn)][0]))
                        secretMessage = AES.encryptBinaryString(secretMessage, AESkeyEncode)
                        mainWindow.listWidget_log.addItem("AES encryption completed: "+ str(addresses[connections.index(conn)][0]))
                        secretMessage = list(map(int, list(secretMessage)))
                    
                    # Convert ASCII to binary 
                    binaryKey = fp.messageToBinary(keyString.decode())
                    binaryKey = binaryKey * int((len(secretMessage) + float(len(secretMessage))/len(binaryKey)) )
    
                    stegoSamples, capacityWarning, infoMessage = GA_encoding(coverSamples, secretMessage, binaryKey, rate, fileType)
                    sockets.send_one_message(conn, "Stats")
                    sockets.send_one_message(conn, infoMessage)

                    
                    mainWindow.listWidget_log.addItem("Embedding completed: " + str(addresses[connections.index(conn)][0]))
                    
                    # Write to the stego audio file in wave format and close the song
                    stegoSamples = np.asarray(stegoSamples, dtype=np.float32, order = 'C')/ 32768.0
                    scWave.write(str(clientNum) + "_StegoFile" + ".wav", rate, stegoSamples)
                    
        
                    # Send to the requested receiver            
                    mainWindow.listWidget_log.addItem("Sending to clients: " + str(addresses[connections.index(conn)][0]))
                    f_send = str(clientNum) + "_StegoFile" + ".wav"
        
                    # Get the connections to send to
                    connToSendTo = []
                    
                    if (toWhom == "P"):
                        howMuch = sockets.recv_one_message(conn)
                        howMuch = int(howMuch)
                        
                        for i in range(howMuch):
                            ip = sockets.recv_one_message(conn)
                            
                            for j in range(0, len(addresses)):
                                if (addresses[j][0] == ip.decode()):
                                    connToSendTo.append(connections[j])
                        
                    elif (toWhom == "C"):
                        connToSendTo.append(conn)
                        
                    elif (toWhom == "CP"):
                        connToSendTo.append(conn)
                        
                        howMuch = sockets.recv_one_message(conn)
                        howMuch = int(howMuch)
                        
                        for i in range(howMuch):
                            ip = sockets.recv_one_message(conn)
                            
                            for j in range(0, len(addresses)):
                                if (addresses[j][0] == ip.decode()):
                                    connToSendTo.append(connections[j])
                                      
                    clients = "Client targets: \n"
                    for i in connToSendTo:
                        clients += "--->" + str(addresses[connections.index(i)][0]) + "\n"
                    
                    mainWindow.listWidget_log.addItem(clients)
                                    
                    for i in connToSendTo:
                        
                        if (capacityWarning == True):
                                sockets.send_one_message(i, 'WARN')  
                                                          
                        with open(f_send, "rb") as f:
                            data = f.read()
                            sockets.send_one_message(i, "RECFILE")
                            sockets.send_one_message(i, '.wav')
                            sockets.send_one_file(i, data)
                            f.close()
                    mainWindow.listWidget_log.addItem("All clients received stego: " + str(addresses[connections.index(conn)][0]))
                        
                    sockets.send_one_message(conn, "SENT_SUCCESS")
    
                # The DWT OBH was selected                
                elif (method.decode() == "DWT"):
                    OBH = int(sockets.recv_one_message(conn).decode())
    
                    mainWindow.listWidget_log.addItem("OBH = " + str(OBH) + ": "  + str(addresses[connections.index(conn)][0]))
                    # Receive the recipients to whom to send to
                    # CP = Client and Peer
                    # P  = Peer
                    # C  = Client
                    toWhom = sockets.recv_one_message(conn)
                    toWhom = toWhom.decode()
                                    
                    # Extract the cover samples from the cover audio file
                    mainWindow.listWidget_log.addItem("Embedding stego: "+ str(addresses[connections.index(conn)][0]))
                    
                    samplesOne, samplesTwo, rate = fp.getWaveSamples(str(clientNum) + ".wav")
                    
                    message = ""
                    
                    if (fileType == ".wav"):
    
                        # Get the audio samples in integer form
                        intSamples = fp.extractWaveMessage(str(clientNum) + "MSG" + fileType)
    
                        # Convert to integer list of bits for embedding
                        message = "".join(intSamples[0])
                        mainWindow.listWidget_log.addItem("AES encryption Starting: "+ str(addresses[connections.index(conn)][0]))
                        message = AES.encryptBinaryString(message, AESkeyEncode)
                        mainWindow.listWidget_log.addItem("AES encryption completed: "+ str(addresses[connections.index(conn)][0]))
                        
                        message = list(map(int, list(message)))
                        
                    else:
                        message = fp.getMessageBits(str(clientNum) + "MSG" + fileType)
                        message = list(map(str, message))
                        message = "".join(message)
                        mainWindow.listWidget_log.addItem("AES encryption Starting: "+ str(addresses[connections.index(conn)][0]))
                        message = AES.encryptBinaryString(message, AESkeyEncode)
                        mainWindow.listWidget_log.addItem("AES encryption completed: "+ str(addresses[connections.index(conn)][0]))
                        message = list(map(int, list(message)))
                        
                    
                    message = "".join(list(map(str, message)))
                
                    originalCoverSamples = deepcopy(samplesOne) 
                  
                    stegoSamples, samplesUsed, capacityWarning = dwtOBH.dwtHaarEncode(samplesOne, message, OBH, 512, fileType)
                    
                    mainWindow.listWidget_log.addItem("Embedding completed: " + str(addresses[connections.index(conn)][0]))
    
      
                    # Get the characteristics of the stego file
                    infoMessage = "Embedded " + str(round(len(message)/samplesUsed, 5)) + " bits per sample on average."
                    infoMessage += "\nSNR of " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] ), 2))
                    infoMessage += ".\nCapacity of " + str(RT.getCapacity(message, samplesUsed, rate)) + " kbps."       
                    sockets.send_one_message(conn, "Stats")
                    sockets.send_one_message(conn, infoMessage)
      
      
                    # Write to the stego audio file in wave format and close the song
                    mainWindow.listWidget_log.addItem("Writing stego to file")
                    stegoSamples = np.asarray(stegoSamples, dtype=np.float32, order = 'C')/32768.0
                    scWave.write(str(clientNum) + "_StegoFile" + ".wav", rate, stegoSamples)
                    mainWindow.listWidget_log.addItem("Done writing stego to file")
        
                    # Send to the requested receiver            
                    mainWindow.listWidget_log.addItem("Sending to clients: " + str(addresses[connections.index(conn)][0]))
                    f_send = str(clientNum) + "_StegoFile" + ".wav"
        
                    # Get the connections to send to
                    connToSendTo = []
                    
                    if (toWhom == "P"):
                        howMuch = sockets.recv_one_message(conn)
                        howMuch = int(howMuch)
                        
                        for i in range(howMuch):
                            ip = sockets.recv_one_message(conn)
                            
                            for j in range(0, len(addresses)):
                                if (addresses[j][0] == ip.decode()):
                                    connToSendTo.append(connections[j])
                        
                    elif (toWhom == "C"):
                        connToSendTo.append(conn)
                        
                    elif (toWhom == "CP"):
                        connToSendTo.append(conn)
                        
                        howMuch = sockets.recv_one_message(conn)
                        howMuch = int(howMuch)
                        
                        for i in range(howMuch):
                            ip = sockets.recv_one_message(conn)
                            
                            for j in range(0, len(addresses)):
                                if (addresses[j][0] == ip.decode()):
                                    connToSendTo.append(connections[j])
                                         
                    clients = "Client targets: \n"
                    for i in connToSendTo:
                        clients += "--->" + str(addresses[connections.index(i)][0]) + "\n"
                    
                    mainWindow.listWidget_log.addItem(clients)
                                    
                    for i in connToSendTo:
                        
                        if (capacityWarning == True):
                                sockets.send_one_message(i, 'WARN')  
                                continue
                          
                        with open(f_send, "rb") as f:
                            data = f.read()
                            sockets.send_one_message(i, "RECFILE")
                            sockets.send_one_message(i, '.wav')
                            sockets.send_one_file(i, data)
                            f.close()
                        
                    mainWindow.listWidget_log.addItem("All clients received stego: " + str(addresses[connections.index(conn)][0]))
    
                    sockets.send_one_message(conn, "SENT_SUCCESS")
                    
                    
                    
                    
                    
                # The DWT OBH was selected                
                elif (method.decode() == "DWT_hybrid"):
                    OBH = int(sockets.recv_one_message(conn).decode())
    
                    mainWindow.listWidget_log.addItem("OBH = " + str(OBH) + ": "  + str(addresses[connections.index(conn)][0]))
                    # Receive the recipients to whom to send to
                    # CP = Client and Peer
                    # P  = Peer
                    # C  = Client
                    toWhom = sockets.recv_one_message(conn)
                    toWhom = toWhom.decode()
                                    
                    # Extract the cover samples from the cover audio file
                    mainWindow.listWidget_log.addItem("Embedding stego: "+ str(addresses[connections.index(conn)][0]))
                    
                    samplesOne, samplesTwo, rate = fp.getWaveSamples(str(clientNum) + ".wav")
                    
                    message = ""
                    
                    if (fileType == ".wav"):
    
                        # Get the audio samples in integer form
                        intSamples = fp.extractWaveMessage(str(clientNum) + "MSG" + fileType)
    
                        # Convert to integer list of bits for embedding
                        message = "".join(intSamples[0])
                        mainWindow.listWidget_log.addItem("AES encryption Starting: "+ str(addresses[connections.index(conn)][0]))
                        message = AES.encryptBinaryString(message, AESkeyEncode)
                        mainWindow.listWidget_log.addItem("AES encryption completed: "+ str(addresses[connections.index(conn)][0]))
                        
                        message = list(map(int, list(message)))
                        
                    else:
                        message = fp.getMessageBits(str(clientNum) + "MSG" + fileType)
                        message = list(map(str, message))
                        message = "".join(message)
                        mainWindow.listWidget_log.addItem("AES encryption Starting: "+ str(addresses[connections.index(conn)][0]))
                        message = AES.encryptBinaryString(message, AESkeyEncode)
                        mainWindow.listWidget_log.addItem("AES encryption completed: "+ str(addresses[connections.index(conn)][0]))
                        message = list(map(int, list(message)))
                        
                    
                    message = "".join(list(map(str, message)))
                
                    originalCoverSamples = deepcopy(samplesOne)
                  
                    stegoSamples, samplesUsed, capacityWarning = dwtHybrid.dwtHybridEncode(samplesOne, message, fileType, OBH)
                    mainWindow.listWidget_log.addItem("Embedding completed: " + str(addresses[connections.index(conn)][0]))
    
      
                    # Get the characteristics of the stego file
                    infoMessage = "Embedded " + str(round(len(message)/samplesUsed, 5)) + " bits per sample on average."
                    infoMessage += "\nSNR of " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] ), 2))
                    infoMessage += ".\nCapacity of " + str(RT.getCapacity(message, samplesUsed, rate)) + " kbps."       
                    sockets.send_one_message(conn, "Stats")
                    sockets.send_one_message(conn, infoMessage)
      
      
      
                    # Write to the stego audio file in wave format and close the song
                    mainWindow.listWidget_log.addItem("Writing stego to file")
                    stegoSamples = np.asarray(stegoSamples, dtype=np.float32, order = 'C')/32768.0
                    scWave.write(str(clientNum) + "_StegoFile" + ".wav", rate, stegoSamples)
                    mainWindow.listWidget_log.addItem("Done writing stego to file")
        
                    # Send to the requested receiver            
                    mainWindow.listWidget_log.addItem("Sending to clients: " + str(addresses[connections.index(conn)][0]))
                    f_send = str(clientNum) + "_StegoFile" + ".wav"
        
                    # Get the connections to send to
                    connToSendTo = []
                    
                    if (toWhom == "P"):
                        howMuch = sockets.recv_one_message(conn)
                        howMuch = int(howMuch)
                        
                        for i in range(howMuch):
                            ip = sockets.recv_one_message(conn)
                            
                            for j in range(0, len(addresses)):
                                if (addresses[j][0] == ip.decode()):
                                    connToSendTo.append(connections[j])
                        
                    elif (toWhom == "C"):
                        connToSendTo.append(conn)
                        
                    elif (toWhom == "CP"):
                        connToSendTo.append(conn)
                        
                        howMuch = sockets.recv_one_message(conn)
                        howMuch = int(howMuch)
                        
                        for i in range(howMuch):
                            ip = sockets.recv_one_message(conn)
                            
                            for j in range(0, len(addresses)):
                                if (addresses[j][0] == ip.decode()):
                                    connToSendTo.append(connections[j])
                                         
                    clients = "Client targets: \n"
                    for i in connToSendTo:
                        clients += "--->" + str(addresses[connections.index(i)][0]) + "\n"
                    
                    mainWindow.listWidget_log.addItem(clients)
                                    
                    for i in connToSendTo:
                          
                          if (capacityWarning == True):
                                sockets.send_one_message(i, 'WARN')  
                                continue
                        
                          with open(f_send, "rb") as f:
                            data = f.read()
                            sockets.send_one_message(i, "RECFILE")
                            sockets.send_one_message(i, '.wav')
                            sockets.send_one_file(i, data)
                            f.close()
                        
                    mainWindow.listWidget_log.addItem("All clients received stego: " + str(addresses[connections.index(conn)][0]))
    
                    sockets.send_one_message(conn, "SENT_SUCCESS")    
                    
                    
                    
                    
                # The DWT scaling selected                
                elif (method.decode() == "DWT_scale"):
                    LSBs = int(sockets.recv_one_message(conn).decode())
    
                    mainWindow.listWidget_log.addItem("LSBs = " + str(LSBs) + ": "  + str(addresses[connections.index(conn)][0]))
                    
                    # Receive the recipients to whom to send to
                    # CP = Client and Peer
                    # P  = Peer
                    # C  = Client
                    toWhom = sockets.recv_one_message(conn)
                    toWhom = toWhom.decode()
                                    
                    # Extract the cover samples from the cover audio file
                    mainWindow.listWidget_log.addItem("Embedding stego: "+ str(addresses[connections.index(conn)][0]))
                    
                    samplesOne, samplesTwo, rate = fp.getWaveSamples(str(clientNum) + ".wav")
                    
                    message = ""
                    
                    if (fileType == ".wav"):
    
                        # Get the audio samples in integer form
                        intSamples = fp.extractWaveMessage(str(clientNum) + "MSG" + fileType)
                        
                        # Convert to integer list of bits for embedding
                        message = "".join(intSamples[0])
                        mainWindow.listWidget_log.addItem("AES encryption Starting: "+ str(addresses[connections.index(conn)][0]))
                        message = AES.encryptBinaryString(message, AESkeyEncode)
                        mainWindow.listWidget_log.addItem("AES encryption completed: "+ str(addresses[connections.index(conn)][0]))
                        
                        message = list(map(int, list(message)))
                        
                    else:
                        message = fp.getMessageBits(str(clientNum) + "MSG" + fileType)
                        message = list(map(str, message))
                        message = "".join(message)
                        mainWindow.listWidget_log.addItem("AES encryption Starting: "+ str(addresses[connections.index(conn)][0]))
                        message = AES.encryptBinaryString(message, AESkeyEncode)
                        mainWindow.listWidget_log.addItem("AES encryption completed: "+ str(addresses[connections.index(conn)][0]))
                        message = list(map(int, list(message)))
                        
                        
                    message = "".join(list(map(str, message)))
                    originalCoverSamples = deepcopy(samplesOne)
                    stegoSamples, samplesUsed, capacityWarning = dwtScale.dwtScaleEncode(samplesOne, message, fileType, LSBs)
                    mainWindow.listWidget_log.addItem("Embedding completed: " + str(addresses[connections.index(conn)][0]))
                    
                    
                    # Get the characteristics of the stego file
                    infoMessage = "Embedded " + str(round(len(message)/samplesUsed, 5)) + " bits per sample on average."
                    infoMessage += "\nSNR of " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] ), 2))
                    infoMessage += ".\nCapacity of " + str(RT.getCapacity(message, samplesUsed, rate)) + " kbps."       
                    sockets.send_one_message(conn, "Stats")
                    sockets.send_one_message(conn, infoMessage)
      
    
                    # Write to the stego audio file in wave format and close the song
                    mainWindow.listWidget_log.addItem("Writing stego to file")
                    stegoSamples = np.asarray(stegoSamples, dtype=np.float32, order = 'C')/32768.0
                    scWave.write(str(clientNum) + "_StegoFile" + ".wav", rate, stegoSamples)
                    mainWindow.listWidget_log.addItem("Done writing stego to file")
        
                    # Send to the requested receiver            
                    mainWindow.listWidget_log.addItem("Sending to clients: " + str(addresses[connections.index(conn)][0]))
                    f_send = str(clientNum) + "_StegoFile" + ".wav"
        
                    # Get the connections to send to
                    connToSendTo = []
                    
                    if (toWhom == "P"):
                        howMuch = sockets.recv_one_message(conn)
                        howMuch = int(howMuch)
                        
                        for i in range(howMuch):
                            ip = sockets.recv_one_message(conn)
                            
                            for j in range(0, len(addresses)):
                                if (addresses[j][0] == ip.decode()):
                                    connToSendTo.append(connections[j])
                        
                    elif (toWhom == "C"):
                        connToSendTo.append(conn)
                        
                    elif (toWhom == "CP"):
                        connToSendTo.append(conn)
                        
                        howMuch = sockets.recv_one_message(conn)
                        howMuch = int(howMuch)
                        
                        for i in range(howMuch):
                            ip = sockets.recv_one_message(conn)
                            
                            for j in range(0, len(addresses)):
                                if (addresses[j][0] == ip.decode()):
                                    connToSendTo.append(connections[j])
                                         
                    clients = "Client targets: \n"
                    for i in connToSendTo:
                        clients += "--->" + str(addresses[connections.index(i)][0]) + "\n"
                    
                    mainWindow.listWidget_log.addItem(clients)
                                    
                    for i in connToSendTo:
                        
                          if (capacityWarning == True):
                                sockets.send_one_message(i, 'WARN')  
                                continue
                        
                          with open(f_send, "rb") as f:
                            data = f.read()
                            sockets.send_one_message(i, "RECFILE")
                            sockets.send_one_message(i, '.wav')
                            sockets.send_one_file(i, data)
                            f.close()
                        
                    mainWindow.listWidget_log.addItem("All clients received stego: " + str(addresses[connections.index(conn)][0]))
    
                    sockets.send_one_message(conn, "SENT_SUCCESS")
    
    
                elif (method.decode() == "DWT_encode"):
                    
                    # Receive the recipients to whom to send to
                    # CP = Client and Peer
                    # P  = Peer
                    # C  = Client
                    toWhom = sockets.recv_one_message(conn)
                    toWhom = toWhom.decode()
                                    
                    # Extract the cover samples from the cover audio file
                    mainWindow.listWidget_log.addItem("Embedding stego: "+ str(addresses[connections.index(conn)][0]))
                    samplesOne, samplesTwo, rate = fp.getWaveSamples(str(clientNum) + ".wav")
                    
                    message = ""
                    if (fileType == ".txt"):
                        
                        messageObject = open(str(clientNum) + "MSG" + fileType, "r")
    
                        # Extract the message as a string of characters
                        message = messageObject.read()
                        messageObject.close()
                        
                    else:
                        # Get the audio samples in integer form
                        intSamples = fp.extractWaveMessage(str(clientNum) + "MSG" + fileType)
                        
                        # Convert to integer list of bits for embedding
                        message = "".join(intSamples[0])
                        alphaMessage = ''
                        
                        # Convert the binary stream to a ASCII string
                        for i in range(0, len(message), 4):
                              alphaMessage += AES.bits2string('0010' + message[i: i + 4])

                            
                    mainWindow.listWidget_log.addItem("Embedding starting: " + str(addresses[connections.index(conn)][0]))  
                    originalCoverSamples = deepcopy(samplesOne)
                    if (fileType == '.txt'):
                          stegoSamples, samplesUsed, capacityWarning = DWTcrypt.dwtEncryptEncode(samplesOne, message, 512, fileType)        
                          
                    else:
                          stegoSamples, samplesUsed, capacityWarning = DWTcrypt.dwtEncryptEncode(samplesOne, alphaMessage, 512, fileType)        
                    mainWindow.listWidget_log.addItem("Embedding completed: " + str(addresses[connections.index(conn)][0]))
                    
                    # Get the characteristics of the stego file
                    infoMessage = "Embedded " + str(round(len(message)/samplesUsed, 5)) + " bits per sample on average."
                    infoMessage += "\nSNR of " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] ), 2))
                    infoMessage += ".\nCapacity of " + str(RT.getCapacity(message*8, samplesUsed, rate)) + " kbps."       
                    sockets.send_one_message(conn, "Stats")
                    sockets.send_one_message(conn, infoMessage)
    
                    # Write to the stego audio file in wave format and close the song
                    mainWindow.listWidget_log.addItem("Writing stego to file")

                    stegoSamples = np.asarray(stegoSamples)
                    stegoSamples = stegoSamples.astype(np.float32, order='C') / 32768.0
                    
                    scWave.write(str(clientNum) + "_StegoFile" + ".wav", rate, stegoSamples)
                    mainWindow.listWidget_log.addItem("Done writing stego to file")
        
                    # Send to the requested receiver            
                    mainWindow.listWidget_log.addItem("Sending to clients: " + str(addresses[connections.index(conn)][0]))
                    f_send = str(clientNum) + "_StegoFile" + ".wav"
        
                    # Get the connections to send to
                    connToSendTo = []
                    
                    if (toWhom == "P"):
                        howMuch = sockets.recv_one_message(conn)
                        howMuch = int(howMuch)
                        
                        for i in range(howMuch):
                            ip = sockets.recv_one_message(conn)
                            
                            for j in range(0, len(addresses)):
                                if (addresses[j][0] == ip.decode()):
                                    connToSendTo.append(connections[j])
                        
                    elif (toWhom == "C"):
                        connToSendTo.append(conn)
                        
                    elif (toWhom == "CP"):
                        connToSendTo.append(conn)
                        
                        howMuch = sockets.recv_one_message(conn)
                        howMuch = int(howMuch)
                        
                        for i in range(howMuch):
                            ip = sockets.recv_one_message(conn)
                            
                            for j in range(0, len(addresses)):
                                if (addresses[j][0] == ip.decode()):
                                    connToSendTo.append(connections[j])
                                         
                    clients = "Client targets: \n"
                    for i in connToSendTo:
                        clients += "--->" + str(addresses[connections.index(i)][0]) + "\n"
                    
                    mainWindow.listWidget_log.addItem(clients)
                                    
                    for i in connToSendTo:
                        
                        if (capacityWarning == True):
                                sockets.send_one_message(i, 'WARN')  
                                continue
                          
                        with open(f_send, "rb") as f:
                            data = f.read()
                            sockets.send_one_message(i, "RECFILE")
                            sockets.send_one_message(i, '.wav')
                            sockets.send_one_file(i, data)
                            f.close()
                        
                    mainWindow.listWidget_log.addItem("All clients received stego: " + str(addresses[connections.index(conn)][0]))
    
                    sockets.send_one_message(conn, "SENT_SUCCESS")
                    
                else:
                    mainWindow.listWidget_log.addItem("Invalid Encoding Method selected.")
                  
                    
            elif (message.decode() == "Decode" and authenticated == True):
                # Receive the message file
                
                mainWindow.listWidget_log.addItem("Receiving stego: " + str(addresses[connections.index(conn)][0]))
                stegoObj = open(str(clientNum) + "Stego" + ".wav", "wb")
                data = sockets.recv_one_message(conn)
                stegoObj.write(data)
                stegoObj.close()
                mainWindow.listWidget_log.addItem("Stego received: " + str(addresses[connections.index(conn)][0]))
    
                AESkeyDecode = sockets.recv_one_message(conn).decode()
                mainWindow.listWidget_log.addItem("AES key received - " + AESkeyDecode + ": " + str(addresses[connections.index(conn)][0]))
    
                method = sockets.recv_one_message(conn)
                
                mainWindow.listWidget_log.addItem("Decoding mode selected - " + method.decode() + ": " + str(addresses[connections.index(conn)][0]))
    
                if (method.decode() == "DWT"):
                    OBH = int(sockets.recv_one_message(conn).decode())
                    mainWindow.listWidget_log.addItem("OBH = " + str(OBH) + ": "  + str(addresses[connections.index(conn)][0]))
    
                    mainWindow.listWidget_log.addItem("Extracting message: "+ str(addresses[connections.index(conn)][0]))
    
                    # Open the steganography file
                    samplesOneStego, samplesTwoStego, rate = fp.getWaveSamples(str(clientNum) + "Stego" + ".wav")
                    samplesOneStego = np.asarray(samplesOneStego, dtype=np.float32, order = 'C')*32768.0
                    
                    # Extract the wave samples from the host signal
                    extractMessage, fileType = dwtOBH.dwtHaarDecode(samplesOneStego, OBH, 512)
                      
                    mainWindow.listWidget_log.addItem("Steganography extracting completed: "+ str(addresses[connections.index(conn)][0]))
                    
                    # Encrypt the secret message
                    mainWindow.listWidget_log.addItem("AES decoding starting: "+ str(addresses[connections.index(conn)][0]))
                    extractMessage = AES.decryptBinaryString(extractMessage, AESkeyDecode)
              
                    if (AES.bits2string(extractMessage) == "WRONG_KEY"):
                        fileType = '.txt'
                        extractMessage = fp.messageToBinary('Unauthorised access.\n Wrong AES password provided')
                                                        
                    mainWindow.listWidget_log.addItem("AES decoding completed: "+ str(addresses[connections.index(conn)][0]))
                    
                    mainWindow.listWidget_log.addItem("Writing message to file " + str(addresses[connections.index(conn)][0]))
    
                    if (fileType == ".wav"):
                        fp.writeWaveMessageToFile(extractMessage, str(clientNum) + "msg" + fileType)
                    
                    else:
                        fp.writeMessageBitsToFile(extractMessage, str(clientNum) + "msg" + fileType)
                        
                    mainWindow.listWidget_log.addItem("Writing message completed " + str(addresses[connections.index(conn)][0]))
                    
                    mainWindow.listWidget_log.addItem("Sending message to client: " + str(addresses[connections.index(conn)][0]))
                    
                    with open(str(clientNum) + "msg" + fileType, "rb") as f:
                        data = f.read()
                        sockets.send_one_message(conn, "RECFILE")
                        sockets.send_one_message(conn, fileType)
                        sockets.send_one_file(conn, data)
                        f.close()
                        
                    mainWindow.listWidget_log.addItem("Client received message: " + str(addresses[connections.index(conn)][0]))
                
                  
                elif (method.decode() == "DWT_hybrid"):
                    OBH = int(sockets.recv_one_message(conn).decode())
                    mainWindow.listWidget_log.addItem("OBH = " + str(OBH) + ": "  + str(addresses[connections.index(conn)][0]))
    
                    mainWindow.listWidget_log.addItem("Extracting message: "+ str(addresses[connections.index(conn)][0]))
    
                    # Open the steganography file
                    samplesOneStego, samplesTwoStego, rate = fp.getWaveSamples(str(clientNum) + "Stego" + ".wav")
                    samplesOneStego = np.asarray(samplesOneStego, dtype=np.float32, order = 'C')*32768.0
                    
                    # Extract the wave samples from the host signal
                    extractMessage, fileType = dwtHybrid.dwtHybridDecode(samplesOneStego, OBH)
                      
                    mainWindow.listWidget_log.addItem("Steganography extracting completed: "+ str(addresses[connections.index(conn)][0]))
                    
                    # Encrypt the secret message
                    mainWindow.listWidget_log.addItem("AES decoding starting: "+ str(addresses[connections.index(conn)][0]))
                    extractMessage = AES.decryptBinaryString(extractMessage, AESkeyDecode)
              
                    if (AES.bits2string(extractMessage) == "WRONG_KEY"):
                        fileType = '.txt'
                        extractMessage = fp.messageToBinary('Unauthorised access.\n Wrong AES password provided')
                                                        
                    mainWindow.listWidget_log.addItem("AES decoding completed: "+ str(addresses[connections.index(conn)][0]))
                    
                    mainWindow.listWidget_log.addItem("Writing message to file " + str(addresses[connections.index(conn)][0]))
    
                    if (fileType == ".wav"):
                        fp.writeWaveMessageToFile(extractMessage, str(clientNum) + "msg" + fileType)
                    
                    else:
                        fp.writeMessageBitsToFile(extractMessage, str(clientNum) + "msg" + fileType)
                        
                    mainWindow.listWidget_log.addItem("Writing message completed " + str(addresses[connections.index(conn)][0]))
                    
                    mainWindow.listWidget_log.addItem("Sending message to client: " + str(addresses[connections.index(conn)][0]))
                    
                    with open(str(clientNum) + "msg" + fileType, "rb") as f:
                        data = f.read()
                        sockets.send_one_message(conn, "RECFILE")
                        sockets.send_one_message(conn, fileType)
                        sockets.send_one_file(conn, data)
                        f.close()
                        
                    mainWindow.listWidget_log.addItem("Client received message: " + str(addresses[connections.index(conn)][0]))  
                  
                  
                  
                elif (method.decode() == "DWT_scale"):
                    LSBs = int(sockets.recv_one_message(conn).decode())
                    mainWindow.listWidget_log.addItem("OBH = " + str(LSBs) + ": "  + str(addresses[connections.index(conn)][0]))
    
                    mainWindow.listWidget_log.addItem("Extracting message: "+ str(addresses[connections.index(conn)][0]))
    
                    samplesOneStego, samplesTwoStego, rate = fp.getWaveSamples(str(clientNum) + "Stego" + ".wav")
                    samplesOneStego = np.asarray(samplesOneStego, dtype=np.float32, order = 'C') * 32768.0
                    
                    extractMessage, fileType = dwtScale.dwtScaleDecode(list(samplesOneStego), LSBs)
                      
                    mainWindow.listWidget_log.addItem("Steganography extracting completed: "+ str(addresses[connections.index(conn)][0]))
                    
                    # Encrypt the secret message
                    mainWindow.listWidget_log.addItem("AES decoding starting: "+ str(addresses[connections.index(conn)][0]))
                    extractMessage = AES.decryptBinaryString(extractMessage, AESkeyDecode)
                    
                    if (AES.bits2string(extractMessage) == "WRONG_KEY"):
                        fileType = '.txt'
                        extractMessage = fp.messageToBinary('Unauthorised access.\n Wrong AES password provided')
                                                        
                    mainWindow.listWidget_log.addItem("AES decoding completed: "+ str(addresses[connections.index(conn)][0]))
                    mainWindow.listWidget_log.addItem("Writing message to file " + str(addresses[connections.index(conn)][0]))
                    
      
                    if (fileType == ".wav"):
                        fp.writeWaveMessageToFile(extractMessage, str(clientNum) + "msg" + fileType)
                    
                    else:
                        fp.writeMessageBitsToFile(extractMessage, str(clientNum) + "msg" + fileType)
                        
                    mainWindow.listWidget_log.addItem("Writing message completed " + str(addresses[connections.index(conn)][0]))
                    
                    mainWindow.listWidget_log.addItem("Sending message to client: " + str(addresses[connections.index(conn)][0]))
                    
                    with open(str(clientNum) + "msg" + fileType, "rb") as f:
                        data = f.read()
                        sockets.send_one_message(conn, "RECFILE")
                        sockets.send_one_message(conn, fileType)
                        sockets.send_one_file(conn, data)
                        f.close()
                        
                    mainWindow.listWidget_log.addItem("Client received message: " + str(addresses[connections.index(conn)][0]))  
                  
                  
                # DWT encryption decoding
                elif(method.decode() == "DWT_encode"):
                    
                    mainWindow.listWidget_log.addItem("Extracting message: "+ str(addresses[connections.index(conn)][0]))
    
                    # Extract the samples from the stego file
                    rate, samples = scWave.read(str(clientNum) + "Stego" + ".wav")
 
                    samples = samples.astype(np.float64, order='C') * 32768.0
                        
                    secretMessage, fileType = DWTcrypt.dwtEncryptDecode(list(samples), 512)
                    mainWindow.listWidget_log.addItem("Steganography extracting completed: "+ str(addresses[connections.index(conn)][0]))
    
                    # Write the message bits to a file and close the steganography file
                    mainWindow.listWidget_log.addItem("Writing message to file " + str(addresses[connections.index(conn)][0]))
                    
                    if (fileType == ".wav"):
                        # Convert to integer list of bits for embedding
                        binMessage = ''
                        # Convert the binary stream to a ASCII string
                        for i in range(0, len(secretMessage)):
                            binMessage += AES.string2bits(secretMessage[i])[4:]                                          
                            
                        fp.writeWaveMessageToFile(binMessage, str(clientNum) + "msg" + fileType)
              
                    else:

                            messageFileObj = open(str(clientNum) + "msg" + fileType, 'w')
                            messageFileObj.write(secretMessage)
                            messageFileObj.close()
                                      
                    
                    
      
                        
                        
                    mainWindow.listWidget_log.addItem("Writing message completed " + str(addresses[connections.index(conn)][0]))
                    mainWindow.listWidget_log.addItem("Sending message to client: " + str(addresses[connections.index(conn)][0]))
    
                    with open(str(clientNum) + "msg" + fileType, "rb") as f:
                        data = f.read()
                        sockets.send_one_message(conn, "RECFILE")
                        sockets.send_one_message(conn, fileType)
                        sockets.send_one_file(conn, data)
                        f.close()
                        
                    mainWindow.listWidget_log.addItem("Client received message: " + str(addresses[connections.index(conn)][0]))
                    
                    
                # Genetic Algorithm decoding
                elif(method.decode() == "GA"):
                    keyString = sockets.recv_one_message(conn)
                    keyString = keyString.decode()
                    mainWindow.listWidget_log.addItem("Key: " + keyString + ": " + str(addresses[connections.index(conn)][0]))
    
                    binaryKey = fp.messageToBinary(keyString)
                    
                    mainWindow.listWidget_log.addItem("Extracting message: "+ str(addresses[connections.index(conn)][0]))
    
                    # Extract the samples from the stego file
                    stegoSamplesOne, stegoSamplesTwo, rate = fp.getWaveSamples(str(clientNum) + "Stego.wav")
                    stegoSamples = np.asarray(stegoSamplesOne, dtype=np.float32, order = 'C') * 32768.0
                    
                    # Get the secret message
                    secretMessage, fileType = GA_decoding(list(stegoSamples), binaryKey)
                    
                    mainWindow.listWidget_log.addItem("Steganography extracting completed: "+ str(addresses[connections.index(conn)][0]))
           
                    # Encrypt the secret message
                    mainWindow.listWidget_log.addItem("AES decoding starting: "+ str(addresses[connections.index(conn)][0]))
                  
                  
                    secretMessage = AES.decryptBinaryString(secretMessage, AESkeyDecode)
                    if (AES.bits2string(secretMessage) == "WRONG_KEY"):
                          fileType = '.txt'
                          secretMessage = fp.messageToBinary('Unauthorised access.\n Wrong AES password provided')
                          
                    mainWindow.listWidget_log.addItem("AES decoding completed: "+ str(addresses[connections.index(conn)][0]))
    
                    
                    # Write the message bits to a file and close the steganography file
                    mainWindow.listWidget_log.addItem("Writing message to file " + str(addresses[connections.index(conn)][0]))
                    if (fileType == ".wav"):
                        fp.writeWaveMessageToFile(secretMessage, str(clientNum) + "msg" + fileType)
                    
                    else:
                        fp.writeMessageBitsToFile(secretMessage, str(clientNum) + "msg" + fileType)
                        
                    mainWindow.listWidget_log.addItem("Writing message completed " + str(addresses[connections.index(conn)][0]))
                    
                    mainWindow.listWidget_log.addItem("Sending message to client: " + str(addresses[connections.index(conn)][0]))
    
                    with open(str(clientNum) + "msg" + fileType, "rb") as f:
                        data = f.read()
                        sockets.send_one_message(conn, "RECFILE")
                        sockets.send_one_message(conn, fileType)
                        sockets.send_one_file(conn, data)
                        f.close()
                        
                    mainWindow.listWidget_log.addItem("Client received message: " + str(addresses[connections.index(conn)][0]))
                    
                    
                    
            elif (message.decode() == "Disconnect"):
                  mainWindow.listWidget_log.addItem("Client " + str(addresses[connections.index(conn)]) + " disconnected")
                  clientsConnected -= 1
                  mainWindow.label_num_clients.setText("Clients connected: " + str(clientsConnected))
                  connections[connections.index(conn)].close()
                  del addresses[connections.index(conn)]
                  del connections[connections.index(conn)]
                  break
                                
            else:
                  mainWindow.listWidget_log.addItem("Server receiving command")
                  mainWindow.listWidget_log.addItem("Command -> " + message.decode())
                  
#        except Exception:
#            mainWindow.listWidget_log.addItem("[-] Client disconnected")
#            clientsConnected -= 1
#            mainWindow.label_num_clients.setText("Clients connected: " + str(clientsConnected))

def acceptClients(param):
      HOST = ""
      mainWindow.listWidget_log.addItem("Server listening thread created")
      global clientsConnected
      global s
      global connections
      global addresses

      while True:
          try:
              s.bind((HOST, int(mainWindow.lineEdit_port.text())))
              s.listen(5)
              break
          except Exception:
              mainWindow.listWidget_log.addItem("Invalid port number specified.")
              s.close()
              return
      
      while True:
          try:
              conn, addr = s.accept()
              s.setblocking(1)  # prevents timeout
              mainWindow.listWidget_log.addItem("Client " + str(addr) + " connected on port " + mainWindow.lineEdit_port.text())
              connections.append(conn)
              addresses.append(addr)
              
              clientThread = threading.Thread(target=threaded_client, args=(connections[-1], addr,))
              clientThread.isDaemon = True
              clientThread.start()
              clientsConnected += 1
              mainWindow.label_num_clients.setText("Clients connected: " + str(clientsConnected))
                              
          except Exception:
                mainWindow.listWidget_log.addItem("Socket unexpectedly closed. Server will shut down")
                s.close()
                break
                
      mainWindow.listWidget_log.addItem("Server ended")   
      mainWindow.label_server_status.setText("Server Status: Off")
        
def startServerThread():
      global s
      global serverThread
      
      serverThread = []
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      serverThread.append(threading.Thread(target=acceptClients, args=(1,)))
      mainWindow.label_server_status.setText("Server Status: On")
      serverThread[-1].isDaemon = True
      serverThread[-1].start()
            
def endServer():
      global s
      global connections
      global addresses
      global serverThread
      global clientsConnected
      global attemptsLeft
      
      for filename in os.listdir():
          if (filename.endswith('.txt') or filename.endswith('.wav')):
              os.unlink(filename)

      mainWindow.label_server_status.setText("Server Status: Off")
      s.close()
      
      for i in connections:
          sockets.send_one_message(i, "Disconnect")
      
      time.sleep(0.1)  
        
      for i in connections:  
          i.close()
      
      del addresses[:]
      del connections[:]
      del serverThread[:]
      
      clientsConnected = 0
      
      mainWindow.label_num_clients.setText("Clients connected: " + str(clientsConnected))

def authenticateServerAccess():
      file = open('UnamePword/username.txt', 'r')
      uName = file.read()
      file.close()
      
      file = open('UnamePword/password.txt', 'r')
      pWord = file.read()
      file.close()
            
      uName = AES.bits2string(AES.decryptBinaryString(uName, mainWindow.lineEdit_username.text()))
      pWord = AES.bits2string(AES.decryptBinaryString(pWord, mainWindow.lineEdit_password.text()))
      
      if (mainWindow.lineEdit_username.text() == uName and mainWindow.lineEdit_password.text() == pWord):
            mainWindow.pushButton_start.setEnabled(True)
            mainWindow.pushButton_stop.setEnabled(True)
            rightUnamePword.emit()
      else:
            wrongUnamePword.emit()
      
def logoff():
    mainWindow.pushButton_start.setEnabled(False)
    mainWindow.pushButton_stop.setEnabled(False)

def change():
      file = open('UnamePword/username.txt', 'r')
      uName = file.read()
      file.close()
      
      file = open('UnamePword/password.txt', 'r')
      pWord = file.read()
      file.close()
            
      uName = AES.bits2string(AES.decryptBinaryString(uName, mainWindow.lineEdit_username.text()))
      pWord = AES.bits2string(AES.decryptBinaryString(pWord, mainWindow.lineEdit_password.text()))
      
      if (mainWindow.lineEdit_username.text() == uName and mainWindow.lineEdit_password.text() == pWord):
            
            newName = mainWindow.lineEdit_new_username.text()
            newPwd = mainWindow.lineEdit_new_password.text()
            
            newName = AES.AESCipher(newName).encrypt(newName)
            newPwd = AES.AESCipher(newPwd).encrypt(newPwd)
            
            file = open('UnamePword/username.txt', 'w')
            file.write(AES.string2bits(newName))
            file.close()
            
            file = open('UnamePword/password.txt', 'w')
            file.write(AES.string2bits(newPwd))
            file.close()
            changeUnamePword.emit()
      else:
            wrongUnamePword.emit()

if __name__ == "__main__":
    
    # Create a QtWidget application
    app = QtWidgets.QApplication(sys.argv)
    
    # Load the user interface designed on Qt Designer
    mainWindow = uic.loadUi("ServerGUI.ui")
    mainWindow.pushButton_start.clicked.connect(startServerThread)
    mainWindow.pushButton_stop.clicked.connect(endServer)
    mainWindow.pushButton_login.clicked.connect(authenticateServerAccess)
    mainWindow.pushButton_logoff.clicked.connect(logoff)
    mainWindow.pushButton_change.clicked.connect(change)
    wrongUnamePword.connect()
    rightUnamePword.connect()
    changeUnamePword.connect()
    # Set the GUI background to specified image
    mainWindow.setStyleSheet("QMainWindow {border-image: url(Media/music.jpg) 0 0 0 0 stretch stretch}")
    
    
    mainWindow.pushButton_start.setEnabled(False)
    mainWindow.pushButton_stop.setEnabled(False)
    
    # Execute and show the user interface
    mainWindow.show()
    app.exec_()