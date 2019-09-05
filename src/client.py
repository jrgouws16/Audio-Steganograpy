# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 20:47:41 2019

@author: Johan Gouws
"""

from PyQt5 import QtWidgets, uic
import socket
import sockets
import fileprocessing as fp
import SignalsAndSlots as SS
import threading
import time

signalSaveFile = SS.fileSaveSigSlot()
msgDelivered = SS.showInfoSigSlot()
msgDelivered.title = "Sent stego success."
msgDelivered.info = "Message was delivered to all clients successfully."

server = []
connectedToServer = False

def connectToServer():
    global server
    global connectedToServer
    
    if (len(server) != 0):
        SS.showErrorMessage("Established Connection","You are already connected to a server.")
        
    else:
        HOST = mainWindow.lineEdit_server_ip.text()
        PORT = int(mainWindow.lineEdit_server_port.text())
        
        s = socket.socket(socket.AF_INET,   socket.SOCK_STREAM)
        
        try:
            s.connect((HOST, PORT))
            server.append(s)  
            mainWindow.label_server_status.setText("Status: Connected")
            connectedToServer = True
           
        except Exception:
              SS.showErrorMessage("Error Connecting", "Server unavailable.")
              s.close()
              del server[:]
     
def disconnectFromServer():
    global connectedToServer
    connectedToServer = False
    sockets.send_one_message(server[-1], "Disconnect")
    time.sleep(0.1)
    server[-1].close()
    del server[:]
    mainWindow.label_server_status.setText("Status: Disonnected")

def fileReceiveThread():
      while True:
        if (len(server) > 0):
            try:
                data = sockets.recv_one_message(server[-1])
                
                if (connectedToServer):
                
                    if (data.decode() == "RECFILE"):
                        data = sockets.recv_one_message(server[-1])
                        signalSaveFile.emit()
                        
                        while (signalSaveFile.setPath == False):
                              continue
                        
                        filepath = signalSaveFile.filePath
                        signalSaveFile.setPath = False
                        f = open(filepath, "wb")
                        f.write(data)
                        f.close()
                        
                    elif (data.decode() == "Disconnect"):
                        server[-1].close()
                        del server[:]
                        mainWindow.label_server_status.setText("Status: Disonnected")
                        
                    elif (data.decode() == "SENT_SUCCESS"):
                        msgDelivered.emit()
                
            except Exception:
                continue

def encode():
    # Send the encode command to the server
    sockets.send_one_message(server[-1], "Encode")    
        
    # Get the cover file name from the line edit box and send to server
    coverFileName = mainWindow.lineEdit_cover.text()
    
    with open(coverFileName, "rb") as f:
        data = f.read()
        sockets.send_one_file(server[0], data)
        f.close()
    
    # Get the message file name from the line edit box and send to server
    messageFileName = mainWindow.lineEdit_message.text()
    
    with open(messageFileName, "rb") as f:
        data = f.read()
        sockets.send_one_file(server[0], data)
        f.close()

    if(mainWindow.radioButton_DWT.isChecked()):
        print("")
            
    # Second method = Genetic Algorithm
    elif(mainWindow.radioButton_GA.isChecked()):
        # Get the string representation of the key in ASCII
        keyString = mainWindow.lineEdit_GA_key.text()
              
        # Send that Genetic algorithm was chosen
        sockets.send_one_message(server[-1], "GA")
        
        # Send the secret key
        sockets.send_one_message(server[-1], keyString)
        
        receivers = []
        
        if (mainWindow.lineEdit_receiver_IP_1.text() != ""):
            receivers.append(mainWindow.lineEdit_receiver_IP_1.text())

        if (mainWindow.lineEdit_receiver_IP_2.text() != ""):
            receivers.append(mainWindow.lineEdit_receiver_IP_2.text())
            
        if (mainWindow.lineEdit_receiver_IP_3.text() != ""):
            receivers.append(mainWindow.lineEdit_receiver_IP_3.text())

        if (mainWindow.lineEdit_receiver_IP_4.text() != ""):
            receivers.append(mainWindow.lineEdit_receiver_IP_4.text())
        
        if (mainWindow.checkBox_peer.isChecked() and mainWindow.checkBox_local.isChecked()):
            # Send to client and peers
            sockets.send_one_message(server[-1], "CP")

            sockets.send_one_message(server[-1], str(len(receivers)))            
                        
            for i in range(0, len(receivers)):
                sockets.send_one_message(server[-1], receivers[i])
            
        elif (mainWindow.checkBox_peer.isChecked()):
            # Send to peers
            sockets.send_one_message(server[-1], "P")
            sockets.send_one_message(server[-1], str(len(receivers)))
            
            for i in range(0, len(receivers)):
                sockets.send_one_message(server[-1], receivers[i])
            
        else:
            # Send to client
            sockets.send_one_message(server[-1], "C")
            
    # If no encoding algorithm is selected, throw an erro message 
    else:
        SS.showErrorMessage("Invalid Encoding Algorithm selected",
                         "Select an encoding algorithm by selecting a radio button")        



# Function for extracting the message using different stegangography algorithms
def decode():
    
    # Send the encode command to the server
    sockets.send_one_message(server[-1], "Decode") 
    
    # Get the filename of the stego audio file
    stegoFileName = mainWindow.lineEdit_stego.text()

    with open(stegoFileName, "rb") as f:
        data = f.read()
        sockets.send_one_file(server[-1], data)
        f.close()
    
    if (mainWindow.radioButton_DWT_3.isChecked()):
        print("")
        
    # Genetic Algorithm decoding
    elif(mainWindow.radioButton_GA_3.isChecked()):
        sockets.send_one_message(server[-1], "GA") 
        
        keyString = mainWindow.lineEdit_GA_key_3.text()
        
        sockets.send_one_message(server[-1], keyString) 
        
    # No radio button selected
    else:
        SS.showErrorMessage("Invalid Encoding Algorithm selected",
                         "Select an encoding algorithm by selecting a radio button")

def setCoverPath():
      mainWindow.lineEdit_cover.setText(fp.openFile())
      
def setMessagePath():
      mainWindow.lineEdit_message.setText(fp.openFile())
      
# Slot to set the file path to get the stego file      
def setStegoPath():
      mainWindow.lineEdit_stego.setText(fp.openFile())

      
def setKey():
    fileName = fp.openFile()
    fileContent = open(fileName, 'r', encoding = 'utf-8')
    mainWindow.lineEdit_GA_key.setText(fileContent.read())      

if __name__ == "__main__":
    # Create a QtWidget application
    app = QtWidgets.QApplication([])

    # Load the user interface designed on Qt Designer
    mainWindow = uic.loadUi("ClientGUI.ui")
    
    # Set the placeholder that will display the cover file path selected
    mainWindow.lineEdit_cover.setPlaceholderText("Path")
    mainWindow.lineEdit_cover.setReadOnly(True)
    
    # Set the placeholder that will display the message file path selected
    mainWindow.lineEdit_message.setPlaceholderText("Path")
    mainWindow.lineEdit_message.setReadOnly(True)
    
    # Set the placeholder for the key of the GA
    mainWindow.lineEdit_GA_key.setPlaceholderText("Insert Key or browse for key file (.txt)")
    
    # Set the placeholder that will display the stego file path selected
    mainWindow.lineEdit_stego.setPlaceholderText("Path")
    mainWindow.lineEdit_stego.setReadOnly(True)
    
    # Guide user to provide values 1, 2, 3 or 4
    mainWindow.lineEdit_OBH_nr_3.setPlaceholderText("OBH")
        
    # Objects to hide at the start of the GUI
    mainWindow.lineEdit_GA_key.hide()
    
    # Hide objects at start
    mainWindow.lineEdit_GA_key.hide()
    mainWindow.pushButton_browse_key.hide()
    mainWindow.lineEdit_OBH.hide()
    
    # Connect the buttons to the appropriate slots
    mainWindow.pushButton_connect.clicked.connect(connectToServer)
    mainWindow.pushButton_encode.clicked.connect(encode)
    mainWindow.pushButton_browse_key.clicked.connect(setKey)
    mainWindow.pushButton_browse_cover.clicked.connect(setCoverPath)
    mainWindow.pushButton_browse_message.clicked.connect(setMessagePath)
    mainWindow.pushButton_disconnect.clicked.connect(disconnectFromServer)
    mainWindow.pushButton_decode.clicked.connect(decode)
    mainWindow.pushButton_browse_stego_3.clicked.connect(setStegoPath)
    
    signalSaveFile.connect()
    msgDelivered.connect()

    # Guide user to provide values 1, 2, 3 or 4
    mainWindow.lineEdit_OBH.setPlaceholderText("OBH")
    
    # Set the progress on the progress bars to 0 to start with
    mainWindow.progressBar_reading.setValue(0)
    mainWindow.progressBar_embedding.setValue(0)
    mainWindow.progressBar_writing.setValue(0)
    mainWindow.progressBar_message.setValue(0)
    mainWindow.progressBar_reading_3.setValue(0)
    mainWindow.progressBar_extracting.setValue(0)
    mainWindow.progressBar_writing_3.setValue(0)    

    recFileThread = threading.Thread(target=fileReceiveThread, args=())
    recFileThread.isDaemon = True
    recFileThread.start()
    
    # Set the GUI background to specified image
    mainWindow.setStyleSheet("QMainWindow {border-image: url(Media/music.jpg) 0 0 0 0 stretch stretch}")
    mainWindow.tabWidget.setStyleSheet("QWidget {background-color: grey }")
    # Execute and show the user interface
    mainWindow.show()
    app.exec()