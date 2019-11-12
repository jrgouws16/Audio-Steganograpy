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
import AES

signalSaveFile = SS.fileSaveSigSlot()
signalSaveTextFile = SS.textFileSaveSigSlot()
signalSaveWavFile = SS.wavFileSaveSigSlot() 
msgDelivered = SS.showInfoSigSlot()
msgDelivered.title = "Sent stego success."
msgDelivered.info = "Message was delivered to all clients successfully."
invalidCover = SS.showInfoSigSlot()
invalidCover.title = "Cover file invalid."
invalidCover.info = "Provide a valid cover wave file."
capacityWarning = SS.showInfoSigSlot()
capacityWarning.title = 'CapacityWarning'
capacityWarning.info = 'The cover file is too small for the message provided'
authenticated = SS.showInfoSigSlot()
authenticated.title = 'Authentication successful'
authenticated.info = 'Username and password entered correctly.'
notAuthenticated = SS.showInfoSigSlot()
notAuthenticated.title = 'Authentication unsuccessful'
notAuthenticated.info = 'Username and password not entered correctly.'

embeddedStats = SS.showInfoSigSlot()
errorMsg = SS.showInfoSigSlot()

server = []
connectedToServer = False
authenticatedByServer = False

def connectToServer():
    global server
    global connectedToServer
    global authenticatedByServer
    
    if (len(server) != 0 and authenticatedByServer == True):
        SS.showErrorMessage("Established Connection","You are already connected to a server.")
        
    elif(len(server) != 0 and authenticatedByServer == False):
        sockets.send_one_message(server[-1], 'Authenticate')
        sockets.send_one_message(server[-1], AES.encryptBinaryString(AES.string2bits(mainWindow.lineEdit_username.text()), mainWindow.lineEdit_username.text()))
        sockets.send_one_message(server[-1], AES.encryptBinaryString(AES.string2bits(mainWindow.lineEdit_password.text()), mainWindow.lineEdit_password.text()))
    
    else:
        HOST = mainWindow.lineEdit_server_ip.text()
        PORT = int(mainWindow.lineEdit_server_port.text())
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
              s.connect((HOST, PORT))
              server.append(s)  
            
              # Send the encode command to the server
              sockets.send_one_message(server[-1], 'Authenticate')
              sockets.send_one_message(server[-1], AES.encryptBinaryString(AES.string2bits(mainWindow.lineEdit_username.text()), mainWindow.lineEdit_username.text()))
              sockets.send_one_message(server[-1], AES.encryptBinaryString(AES.string2bits(mainWindow.lineEdit_password.text()), mainWindow.lineEdit_password.text()))
            
              mainWindow.label_server_status.setText("Status: Connected")
              connectedToServer = True
           
                  
            
        except Exception:
              SS.showErrorMessage("Error Connecting", "Server unavailable.")
              s.close()
              del server[:]

def disconnectFromServer():
    global connectedToServer
    global authenticatedByServer
    
    connectedToServer = False
    sockets.send_one_message(server[-1], "Disconnect")
    time.sleep(0.1)
    server[-1].close()
    del server[:]
    mainWindow.label_server_status.setText("Status: Disonnected")

def fileReceiveThread():
      global authenticatedByServer
      
      while True:
        if (len(server) > 0):
            try:
                data = sockets.recv_one_message(server[-1])
                
                if (connectedToServer):
                
                    if (data.decode() == "RECFILE"):
                        
                        fileType = sockets.recv_one_message(server[-1]).decode()
                        data = sockets.recv_one_message(server[-1])
                        
                        if (fileType == '.wav'):
                            signalSaveWavFile.emit()
                        
                            while (signalSaveWavFile.setPath == False):
                                  continue
                            
                            filepath = signalSaveWavFile.filePath
                            signalSaveWavFile.setPath = False
                            f = open(filepath, "wb")
                            f.write(data)
                            f.close()
                            
                        elif (fileType == '.txt'):
                            signalSaveTextFile.emit()
                        
                            while (signalSaveTextFile.setPath == False):
                                  continue
                            
                            filepath = signalSaveTextFile.filePath
                            signalSaveTextFile.setPath = False
                            f = open(filepath, "wb")
                            f.write(data)
                            f.close()
                        
                                             
                    elif (data.decode() == "WARN"):
                        capacityWarning.emit()
                        
                    elif (data.decode() == "Stats"):
                        embeddedStats.title = 'Steganographic file results'
                        embeddedStats.info = sockets.recv_one_message(server[-1]).decode()
                        embeddedStats.emit()
                        
                    elif (data.decode() == "Capacity"):
                        capacity = sockets.recv_one_message(server[-1])
                        invalidCover.title = "Capacity of cover file."
                        invalidCover.info = "The provided cover file has a capacity of " + capacity.decode() + " bits."
                        invalidCover.emit()

                        
                    elif (data.decode() == "Disconnect"):
                        server[-1].close()
                        del server[:]
                        authenticatedByServer = False
                        mainWindow.label_server_status.setText("Status: Disonnected")
                      
                        
                    elif (data.decode() == "SENT_SUCCESS"):
                        msgDelivered.emit()
                        
                    elif (data.decode() == "Authenticated"):
                          authenticated.emit()
                          authenticatedByServer = True
                          mainWindow.pushButton_cover_capacity.setEnabled(True)
                          mainWindow.pushButton_decode.setEnabled(True)
                          mainWindow.pushButton_encode.setEnabled(True)

                          
                    elif (data.decode() == "Not_authenticated"):
                          attemptsLeft = sockets.recv_one_message(server[-1]).decode()
                          authenticatedByServer = False
                          
                          if (attemptsLeft == '0'):
                                notAuthenticated.info = "You have no attempts left and are blocked from the server"
                          
                          else:
                                notAuthenticated.info = 'Wrong username and password enetered.\nAttempts left:'+ str(attemptsLeft)
                          
                          notAuthenticated.emit()
                
            except Exception:
                continue

def encode():
    
    try:
        
        # Get the cover file name from the line edit box and send to server
        coverFileName = mainWindow.lineEdit_cover.text()
        
        # Error checking if files for cover file. Valid and file type.
        if (coverFileName.split('.')[-1] != "wav"):
            raise Exception('The cover file is invalid. Only wave files allowed.')
        
        # Get the message file name from the line edit box and send to server
        messageFileName = mainWindow.lineEdit_message.text()
        
        # Error checking if files for message file. Valid and file type.
        if (messageFileName.split('.')[-1] != "wav" and messageFileName.split('.')[-1] != "txt" ):
            raise Exception('The message file is invalid. Only .txt and .wav files allowed.')
            
        # Error checking if a valid method was selected
        if (not (mainWindow.radioButton_DWT.isChecked() or mainWindow.radioButton_GA.isChecked() or mainWindow.radioButton_dwt_encoding.isChecked() or mainWindow.radioButton_dwt_scaling_encode.isChecked() or mainWindow.radioButton_DWT_hybrid_encode.isChecked())):
            raise Exception('Select an encoding method.')
        
        # Check if the order of bits or key was supplied
        if (mainWindow.radioButton_DWT.isChecked() and mainWindow.lineEdit_OBH.text() == ""):
            raise Exception('Provide a valid OBH for DWT encoding.')
        
        if (mainWindow.radioButton_DWT_hybrid_encode.isChecked() and mainWindow.lineEdit_OBH_hybrid_encode.text() == ""):
            raise Exception('Provide a valid OBH for DWT hybrid encoding.')    
            
        if (mainWindow.radioButton_GA.isChecked() and mainWindow.lineEdit_GA_key.text() == ""):
            raise Exception('Provide a valid key for GA encoding.')
        
        if (mainWindow.lineEdit_AES_encode.text() == ""):
            raise Exception('Provide a non-empty string for the AES key')
            
        if (mainWindow.label_server_status.text() == "Status: Disonnected"):
            raise Exception('You are not connected to a server.')
     
        
        # Send the encode command to the server
        sockets.send_one_message(server[-1], "Encode")    
        
        # Send the cover file
        with open(coverFileName, "rb") as f:
            data = f.read()
            sockets.send_one_file(server[0], data)
            f.close()
        
        # Send the message file
        if (messageFileName.split('.')[-1] == "wav"):
            sockets.send_one_message(server[-1], ".wav")
            
        elif (messageFileName.split('.')[-1] == "txt"):
            sockets.send_one_message(server[-1], ".txt")
        
        # Send the message file
        with open(messageFileName, "rb") as f:
            data = f.read()
            sockets.send_one_file(server[0], data)
            f.close()
    
        # Send the AES encryption key
        sockets.send_one_message(server[-1], mainWindow.lineEdit_AES_encode.text())
    
        if(mainWindow.radioButton_DWT.isChecked()):
            # Send that DWT method was chosen
            sockets.send_one_message(server[-1], "DWT")
                    
            # Get the order of bits to hold in the coefficients
            OBH = mainWindow.lineEdit_OBH.text()
            
            # Send the order of bits to hold
            sockets.send_one_message(server[-1], OBH)
            
        elif(mainWindow.radioButton_DWT_hybrid_encode.isChecked()):
            # Send that DWT method was chosen
            sockets.send_one_message(server[-1], "DWT_hybrid")
                    
            # Get the order of bits to hold in the coefficients
            OBH = mainWindow.lineEdit_OBH_hybrid_encode.text()
            
            # Send the order of bits to hold
            sockets.send_one_message(server[-1], OBH)
            
        elif(mainWindow.radioButton_dwt_scaling_encode.isChecked()):
            # Send that DWT method was chosen
            sockets.send_one_message(server[-1], "DWT_scale")
                    
            # Get the order of bits to hold in the coefficients
            LSBs = mainWindow.lineEdit_dwt_scale_encoding_LSB.text()
            
            # Send the order of bits to hold
            sockets.send_one_message(server[-1], LSBs)
            
                
        # Second method = Genetic Algorithm
        elif(mainWindow.radioButton_GA.isChecked()):
            # Get the string representation of the key in ASCII
            keyString = mainWindow.lineEdit_GA_key.text()
                  
            # Send that Genetic algorithm was chosen
            sockets.send_one_message(server[-1], "GA")
            
            # Send the secret key
            sockets.send_one_message(server[-1], keyString)
            
        # Third method = DWT encoding method for text
        elif(mainWindow.radioButton_dwt_encoding.isChecked()):
            # Send that Genetic algorithm was chosen
            sockets.send_one_message(server[-1], "DWT_encode")
            
        
        # If no encoding algorithm is selected, throw an erro message 
        else:
            SS.showErrorMessage("Invalid Encoding Algorithm selected",
                             "Select an encoding algorithm by selecting a radio button")  
        
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
              
        
    except Exception as error:
        errorMsg.title = "Invalid user input."
        errorMsg.info = str(error)
        
        if (str(error) == "list index out of range"):
            errorMsg.title = "Server error."
            errorMsg.info = "Connect to a valid server."
        
        errorMsg.emit()

        
        
# Function for extracting the message using different stegangography algorithms
def decode():
    
    try:
        # Get the filename of the stego audio file
        stegoFileName = mainWindow.lineEdit_stego.text()

        # Error checking of file for stego file. Valid and file type.
        if (stegoFileName.split('.')[-1] != "wav"):
            raise Exception('The stego file is invalid. Only wave files allowed.')
            
        # Error checking if a valid method was selected
        if (not (mainWindow.radioButton_DWT_3.isChecked() or mainWindow.radioButton_GA_3.isChecked() or mainWindow.radioButton_dwt_decoding.isChecked() or mainWindow.radioButton_dwt_scaling_decode.isChecked() or mainWindow.radioButton_DWT_hybrid_decode.isChecked())):
            raise Exception('Select a decoding method.')
        
        # Check if the order of bits or key was supplied
        if (mainWindow.radioButton_DWT_3.isChecked() and mainWindow.lineEdit_OBH_nr_3.text() == ""):
            raise Exception('Provide a valid OBH for DWT decoding.')
        
        if (mainWindow.radioButton_DWT_hybrid_decode.isChecked() and mainWindow.lineEdit_OBH_hybrid_decode.text() == ""):
            raise Exception('Provide a valid OBH for DWT hybrid decoding.')
         
            
        if (mainWindow.radioButton_GA_3.isChecked() and mainWindow.lineEdit_GA_key_3.text() == ""):
            raise Exception('Provide a valid key for GA decoding.')
                
        if (mainWindow.lineEdit_AES_decode.text() == ""):
            raise Exception('Provide a non-empty string for the AES key')
        
        if (mainWindow.label_server_status.text() == "Status: Disonnected"):
            raise Exception('You are not connected to a server.')
            
        # Send the encode command to the server
        sockets.send_one_message(server[-1], "Decode") 
                
        # Send the stego file
        with open(stegoFileName, "rb") as f:
            data = f.read()
            sockets.send_one_file(server[-1], data)
            f.close()
        
        # Send the AES encryption key
        sockets.send_one_message(server[-1], mainWindow.lineEdit_AES_decode.text())
        
        # Discrete haar wavelet transform decoding
        if (mainWindow.radioButton_DWT_3.isChecked()):
            # Send the DWT method
            sockets.send_one_message(server[-1], "DWT") 
            
            # Get the order of bits to hold in the coefficients
            OBH = mainWindow.lineEdit_OBH_nr_3.text()
            
            # Send the order of bits to hold
            sockets.send_one_message(server[-1], OBH)
        
        elif (mainWindow.radioButton_DWT_hybrid_decode.isChecked()):
            # Send the DWT method
            sockets.send_one_message(server[-1], "DWT_hybrid") 
            
            # Get the order of bits to hold in the coefficients
            OBH = mainWindow.lineEdit_OBH_hybrid_decode.text()
            
            # Send the order of bits to hold
            sockets.send_one_message(server[-1], OBH) 
            
        elif (mainWindow.radioButton_dwt_scaling_decode.isChecked()):
            # Send the DWT method
            sockets.send_one_message(server[-1], "DWT_scale") 
            
            # Get the order of bits to hold in the coefficients
            LSBs = mainWindow.lineEdit_dwt_scale_decoding_LSB.text()
            
            # Send the order of bits to hold
            sockets.send_one_message(server[-1], LSBs)
            
        # Genetic Algorithm decoding
        elif(mainWindow.radioButton_GA_3.isChecked()):
            sockets.send_one_message(server[-1], "GA") 
            
            # Send the key
            keyString = mainWindow.lineEdit_GA_key_3.text()
            sockets.send_one_message(server[-1], keyString) 
            
        elif (mainWindow.radioButton_dwt_decoding.isChecked()):
            sockets.send_one_message(server[-1], "DWT_encode") 
            
            
    except Exception as error:
        errorMsg.title = "Invalid user input."
        errorMsg.info = str(error)
        errorMsg.emit()

def getCoverCapacity():
    # Get the cover file name from the line edit box and send to server
    coverFileName = mainWindow.lineEdit_cover.text()
    
    # Error checking if files for cover file. Valid and file type.
    if (coverFileName.split('.')[-1] != "wav"):
        invalidCover.title = "Cover file invalid."
        invalidCover.info = "Provide a valid cover wave file."
        invalidCover.emit()
        return
    
    if ( not (mainWindow.radioButton_DWT.isChecked() or mainWindow.radioButton_GA.isChecked() or mainWindow.radioButton_dwt_scaling_encode.isChecked() or mainWindow.radioButton_dwt_encoding.isChecked() or mainWindow.radioButton_DWT_hybrid_encode.isChecked())):    
        invalidCover.title = "Invalid method selected."
        invalidCover.info = "Please select either DWT or GA encoding."
        invalidCover.emit()
        return
    
    # Check if the order of bits or key was supplied
    if (mainWindow.radioButton_DWT.isChecked() and mainWindow.lineEdit_OBH.text() == ""):
        invalidCover.title = "Invalid OBH provided."
        invalidCover.info = "Please select provide an integer for the OBH."
        invalidCover.emit()
        return
    
    # Check if the order of bits or key was supplied
    if (mainWindow.radioButton_DWT_hybrid_encode.isChecked() and mainWindow.lineEdit_OBH_hybrid_encode.text() == ""):
        invalidCover.title = "Invalid OBH provided."
        invalidCover.info = "Please select provide an integer for the OBH."
        invalidCover.emit()
        return
    
    # Send the start of a capacity message
    sockets.send_one_message(server[-1], "Capacity")
        
    # Send the cover file
    with open(coverFileName, "rb") as f:
        data = f.read()
        sockets.send_one_file(server[0], data)
        f.close()

    if (mainWindow.radioButton_DWT.isChecked()):
        sockets.send_one_message(server[0], "DWT")
        sockets.send_one_message(server[0], mainWindow.lineEdit_OBH.text())

    elif (mainWindow.radioButton_DWT_hybrid_encode.isChecked()):
        sockets.send_one_message(server[0], "DWT_hybrid")
        sockets.send_one_message(server[0], mainWindow.lineEdit_OBH_hybrid_encode.text())
        
    elif (mainWindow.radioButton_dwt_scaling_encode.isChecked()):
        sockets.send_one_message(server[0], "DWT_scale")  
        sockets.send_one_message(server[0], mainWindow.lineEdit_dwt_scale_encoding_LSB.text())
    
    elif ( mainWindow.radioButton_dwt_encoding.isChecked()):
        sockets.send_one_message(server[0], "DWT_encode")
        
    else:
        sockets.send_one_message(server[0], "GA")
        
def setCoverPath():
      mainWindow.lineEdit_cover.setText(fp.openFile())
      
def setMessagePath():
      mainWindow.lineEdit_message.setText(fp.openFile())
      
# Slot to set the file path to get the stego file      
def setStegoPath():
      mainWindow.lineEdit_stego.setText(fp.openFile())
      
def setEncryptionKeyAES():
    fileName = fp.openFile()
    fileContent = open(fileName, 'r', encoding = 'utf-8')
    mainWindow.lineEdit_AES_encode.setText(fileContent.read())

def setDecryptionKeyAES():
    fileName = fp.openFile()
    fileContent = open(fileName, 'r', encoding = 'utf-8')
    mainWindow.lineEdit_AES_decode.setText(fileContent.read())
      
def setKey():
    fileName = fp.openFile()
    fileContent = open(fileName, 'r', encoding = 'utf-8')
    mainWindow.lineEdit_GA_key.setText(fileContent.read())   
    
def setKeyDecode():
    fileName = fp.openFile()
    fileContent = open(fileName, 'r', encoding = 'utf-8')
    mainWindow.lineEdit_GA_key_3.setText(fileContent.read())   
    

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
    mainWindow.lineEdit_GA_key_3.setPlaceholderText("Insert Key or browse for key file (.txt)")

    # Set the placeholder that will display the stego file path selected
    mainWindow.lineEdit_stego.setPlaceholderText("Path")
    mainWindow.lineEdit_stego.setReadOnly(True)
    
    mainWindow.lineEdit_OBH_nr_3.setPlaceholderText("OBH")
    mainWindow.lineEdit_OBH_hybrid_decode.setPlaceholderText("OBH")
    mainWindow.lineEdit_OBH_hybrid_encode.setPlaceholderText("OBH")
    
    mainWindow.lineEdit_dwt_scale_encoding_LSB.setPlaceholderText("LSB's")
    mainWindow.lineEdit_dwt_scale_decoding_LSB.setPlaceholderText("LSB's")
        
    # Objects to hide at the start of the GUI
    mainWindow.lineEdit_GA_key.hide()
    
    # Hide objects at start
    mainWindow.lineEdit_GA_key.hide()
    mainWindow.pushButton_browse_key.hide()
    mainWindow.pushButton_browse_key_3.hide()
    mainWindow.lineEdit_OBH.hide()
    mainWindow.lineEdit_OBH_nr_3.hide()
    mainWindow.lineEdit_GA_key_3.hide()
    mainWindow.lineEdit_dwt_scale_encoding_LSB.hide()
    mainWindow.lineEdit_dwt_scale_decoding_LSB.hide()
    mainWindow.lineEdit_OBH_hybrid_decode.hide()
    mainWindow.lineEdit_OBH_hybrid_encode.hide()
    

    # Connect the buttons to the appropriate slots
    mainWindow.pushButton_connect.clicked.connect(connectToServer)
    mainWindow.pushButton_encode.clicked.connect(encode)
    mainWindow.pushButton_browse_key.clicked.connect(setKey)
    mainWindow.pushButton_browse_key_3.clicked.connect(setKeyDecode)
    mainWindow.pushButton_browse_cover.clicked.connect(setCoverPath)
    mainWindow.pushButton_browse_message.clicked.connect(setMessagePath)
    mainWindow.pushButton_disconnect.clicked.connect(disconnectFromServer)
    mainWindow.pushButton_decode.clicked.connect(decode)
    mainWindow.pushButton_browse_stego_3.clicked.connect(setStegoPath)
    mainWindow.pushButton_cover_capacity.clicked.connect(getCoverCapacity)
    mainWindow.pushButton_AES_encode.clicked.connect(setEncryptionKeyAES)
    mainWindow.pushButton_AES_decode.clicked.connect(setDecryptionKeyAES)
    
    signalSaveFile.connect()
    signalSaveTextFile.connect()
    signalSaveWavFile.connect()
    msgDelivered.connect()
    errorMsg.connect()
    invalidCover.connect()
    capacityWarning.connect()
    embeddedStats.connect()
    authenticated.connect()
    notAuthenticated.connect()

    # Guide user to provide values 1, 2, 3 or 4
    mainWindow.lineEdit_OBH.setPlaceholderText("OBH")
    
    recFileThread = threading.Thread(target=fileReceiveThread, args=())
    recFileThread.isDaemon = True
    recFileThread.start()
    
    # Set the GUI background to specified image
    mainWindow.setStyleSheet("QMainWindow {border-image: url(Media/music.jpg) 0 0 0 0 stretch stretch}")
    mainWindow.tabWidget.setStyleSheet("QWidget {background-color: white }")

    mainWindow.pushButton_encode.setEnabled(False)
    mainWindow.pushButton_cover_capacity.setEnabled(False)
    mainWindow.pushButton_decode.setEnabled(False)

    # Execute and show the user interface
    mainWindow.show()
    app.exec()