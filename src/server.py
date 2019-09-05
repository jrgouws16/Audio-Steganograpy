# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 20:47:42 2019

@author: Johan Gouws
"""
from PyQt5 import QtWidgets, uic
import socket
import threading
import sys
import fileprocessing as fp
import sockets
from copy import deepcopy
import geneticAlgorithm as GA
import dwtFirstPrinciples as DWT
import ResultsAndTesting as RT
import wave
import os
import time


serverThread = []
connections = []
addresses = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Function for encoding using the standard LSB encoding algorithm
def GA_encoding(coverSamples, secretMessage, key, songObj):
        originalCoverSamples = deepcopy(coverSamples[0])

        for i in range(0, len(coverSamples[0])):
            coverSamples[0][i] = "{0:016b}".format(coverSamples[0][i])

        secretMessage = "".join(map(str,secretMessage))
    
        # Provide first audio channel samples and message samples to encode 
        stegoSamples, samplesUsed, bitsInserted = GA.insertMessage(coverSamples[0], key, "".join(map(str, secretMessage)))
             
        # Convert the binary audio samples to decimal samples
        for i in range(0, len(stegoSamples)):
            stegoSamples[i] = int(stegoSamples[i], 2)
            
        # Get the characteristics of the stego file
        infoMessage = "Embedded " + str(bitsInserted) + " bits into " + str(samplesUsed) + " samples."
        infoMessage += "\nSNR of " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] ), 2))
        
        frameRate = songObj.getframerate() 
        
        infoMessage += ".\nCapacity of " + str(round((len(secretMessage)/(samplesUsed/frameRate))/1000, 2)) + " kbps."       
            
        # Show the results of the stego quality of the stego file
        mainWindow.listWidget_log.addItem(infoMessage)
                
        return stegoSamples   
    
# Function to extract the message from the stego file making use of 
# Genetic Algorithm
def GA_decoding(stegoSamples, key):
   
    # Convert integer samples to binary samples
    for i in range(0, len(stegoSamples[0])):
        stegoSamples[0][i] = "{0:016b}".format(stegoSamples[0][i])
        
    # Extract secret message
    secretMessage = GA.extractMessage(stegoSamples[0], key)
        
    return secretMessage
   

def threaded_client(conn, clientNum):
    mainWindow.listWidget_log.addItem("Client thread created successfully")  
    while True:
        #try:
        
        message = sockets.recv_one_message(conn)
        
        if (message == None):
              break
          
        # If it is needed to encode the message into the audio    
        elif (message.decode() == "Encode"):
            mainWindow.listWidget_log.addItem("Client requested encoding.")
            
            # Receive the audio cover file
            mainWindow.listWidget_log.addItem("Receiving cover audio.")
            song = open(str(clientNum) + ".wav", "wb")
            data = sockets.recv_one_message(conn)
            song.write(data)
            song.close()
            mainWindow.listWidget_log.addItem("Done receiving cover audio.")
            
            # Receive the message file
            mainWindow.listWidget_log.addItem("Receiving message file.")
            secretMessageObj = open(str(clientNum) + ".txt", "wb")
            data = sockets.recv_one_message(conn)
            secretMessageObj.write(data)
            secretMessageObj.close()
            mainWindow.listWidget_log.addItem("Done receiving message file.")
            
            # Receive the encoding method
            method = sockets.recv_one_message(conn)
            mainWindow.listWidget_log.addItem("Embedding type: " + method.decode() )
            
            if (method.decode() == "GA"):
                stegoSamples = []
    
                # Get the string representation of the key in ASCII
                keyString = sockets.recv_one_message(conn)
                mainWindow.listWidget_log.addItem("GA key: " + keyString.decode())
                
                # Receive the recipients to whom to send to
                # CP = Client and Peer
                # P  = Peer
                # C  = Client
                toWhom = sockets.recv_one_message(conn)
                toWhom = toWhom.decode()
                                
                # Extract the cover samples from the cover audio file
                mainWindow.listWidget_log.addItem("Extracting cover samples.")
                song = wave.open(str(clientNum) + ".wav", "rb")
                coverSamples = fp.extractWaveSamples(song)
                mainWindow.listWidget_log.addItem("Done extracting samples.")
                
                # Extract the message bits from the message file
                mainWindow.listWidget_log.addItem("Extracting bits from message.")
                secretMessage = fp.getMessageBits(str(clientNum) + ".txt")
                mainWindow.listWidget_log.addItem("Done xtracting bits from message.")
                                
                # Convert ASCII to binary 
                binaryKey = fp.messageToBinary(keyString.decode()) 
                binaryKey = binaryKey * int((len(secretMessage) + float(len(secretMessage))/len(binaryKey)) )

                mainWindow.listWidget_log.addItem("Embedding bits")
                stegoSamples = GA_encoding(coverSamples, secretMessage, binaryKey, song)
                mainWindow.listWidget_log.addItem("Success in embedding bits")
                
                # Write to the stego audio file in wave format and close the song
                mainWindow.listWidget_log.addItem("Writing stego to file")
                fp.writeStegoToFile(str(clientNum) + "_StegoFile" + ".wav", song.getparams(), stegoSamples)
                mainWindow.listWidget_log.addItem("Done writing stego to file")
                song.close()
    
                # Send to the requested receiver            
                mainWindow.listWidget_log.addItem("Sending stego to client")
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
                                                    
                for i in connToSendTo:
                    with open(f_send, "rb") as f:
                        data = f.read()
                        sockets.send_one_message(i, "RECFILE")
                        sockets.send_one_file(i, data)
                        f.close()
                    mainWindow.listWidget_log.addItem("Sent stego to client success")
                    
                sockets.send_one_message(conn, "SENT_SUCCESS")

                
            elif (method.decode() == "DWT"):
                OBH = int(sockets.recv_one_message(conn).decode())

                # Receive the recipients to whom to send to
                # CP = Client and Peer
                # P  = Peer
                # C  = Client
                toWhom = sockets.recv_one_message(conn)
                toWhom = toWhom.decode()
                                
                # Extract the cover samples from the cover audio file
                mainWindow.listWidget_log.addItem("Extracting cover samples.")
                song = wave.open(str(clientNum) + ".wav", "rb")
                samplesOne, samplesTwo = fp.extractWaveSamples(song)
                mainWindow.listWidget_log.addItem("Done extracting samples.")
                
                # Extract the message bits from the message file
                mainWindow.listWidget_log.addItem("Extracting bits from message.")
                message = fp.getMessageBits(str(clientNum) + ".txt")
                message = "".join(list(map(str, message)))
                mainWindow.listWidget_log.addItem("Done xtracting bits from message.")
  
                stegoSamples, samplesUsed = DWT.dwtHaarEncode(samplesOne, message, OBH, 2048)
                  
                # Write to the stego audio file in wave format and close the song
                mainWindow.listWidget_log.addItem("Writing stego to file")
                fp.writeStegoToFile(str(clientNum) + "_StegoFile" + ".wav", song.getparams(), stegoSamples)
                mainWindow.listWidget_log.addItem("Done writing stego to file")
                song.close()
    
                # Send to the requested receiver            
                mainWindow.listWidget_log.addItem("Sending stego to client")
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
                                                    
                for i in connToSendTo:
                    with open(f_send, "rb") as f:
                        data = f.read()
                        sockets.send_one_message(i, "RECFILE")
                        sockets.send_one_file(i, data)
                        f.close()
                    mainWindow.listWidget_log.addItem("Sent stego to client success")
                    
                sockets.send_one_message(conn, "SENT_SUCCESS")

                
            else:
                mainWindow.listWidget_log.addItem("Invalid Encoding Method selected.")
              
                
        elif (message.decode() == "Decode"):

            mainWindow.listWidget_log.addItem("Receiving stego file.")
            stegoObj = open(str(clientNum) + "Stego" + ".wav", "wb")
            data = sockets.recv_one_message(conn)
            stegoObj.write(data)
            stegoObj.close()
            mainWindow.listWidget_log.addItem("Done receiving stego file.")

            method = sockets.recv_one_message(conn)
            if (method.decode() == "DWT"):
                print("")
                
            # Genetic Algorithm decoding
            elif(method.decode() == "GA"):
                
                keyString = sockets.recv_one_message(conn)
                keyString = keyString.decode()
                
                binaryKey = fp.messageToBinary(keyString)
                
                # Open the steganography file
                stego = wave.open(str(clientNum) + "Stego" + ".wav", mode='rb')
                
                # Extract the samples from the stego file
                stegoSamples = fp.extractWaveSamples(stego)
                
                # Get the secret message
                secretMessage = GA_decoding(stegoSamples, binaryKey)
                                    
                # Write the message bits to a file and close the steganography file
                fp.writeMessageBitsToFile(secretMessage, str(clientNum) + "msg" + ".txt")
                
                with open(str(clientNum) + "msg" + ".txt", "rb") as f:
                    data = f.read()
                    sockets.send_one_message(conn, "RECFILE")
                    sockets.send_one_file(conn, data)
                    f.close()
                mainWindow.listWidget_log.addItem("Sent message to client success")
                
                
                
        elif (message.decode() == "Disconnect"):
              mainWindow.listWidget_log.addItem("Client " + str(addresses[connections.index(conn)]) + " disconnected")
              connections[connections.index(conn)].close()
              del addresses[connections.index(conn)]
              del connections[connections.index(conn)]
              break
                            
        else:
              mainWindow.listWidget_log.addItem("Server receiving command")
              mainWindow.listWidget_log.addItem("Command -> " + message.decode())
              
        #except Exception:
        #    mainWindow.listWidget_log.addItem("[-] Client disconnected")


def acceptClients(param):
      HOST = ""
      mainWindow.listWidget_log.addItem("Server listening thread created")
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
      
if __name__ == "__main__":
    
    # Create a QtWidget application
    app = QtWidgets.QApplication(sys.argv)
    
    # Load the user interface designed on Qt Designer
    mainWindow = uic.loadUi("ServerGUI.ui")
    mainWindow.pushButton_start.clicked.connect(startServerThread)
    mainWindow.pushButton_stop.clicked.connect(endServer)
    
    
    # Set the GUI background to specified image
    mainWindow.setStyleSheet("QMainWindow {border-image: url(Media/music.jpg) 0 0 0 0 stretch stretch}")
    
    # Execute and show the user interface
    mainWindow.show()
    app.exec_()
      
      
      
      
      
      
      
      
      
      