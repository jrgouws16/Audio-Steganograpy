# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 20:47:41 2019

@author: Johan Gouws
"""

from PyQt5 import QtWidgets, uic
import socket
import sockets
import threading
import fileprocessing as fp
import SignalsAndSlots as SS
import wave

server = []

'''


HOST = 'localhost'

s = socket.socket(socket.AF_INET,   socket.SOCK_STREAM)
# Port to connect to
PORT = 3000

try:
    s.connect((HOST, PORT))
    print("[+] Connected with Server")
    
    sockets.send_one_message(s, "My name is Johan")
      
    sockets.send_one_message(s, "RECFILE")
      
    f_send = "Media/send.pdf"
      
    # open file
    with open(f_send, "rb") as f:
        print("[+] Sending file...")
        data = f.read()
        sockets.send_one_file(s, data)
        f.close()
      
     
    sockets.send_one_message(s, "Disconnect")


    s.close()
    
except Exception:
      print("Client Socket Error")
      s.close()
'''

def connectToServer():
    HOST = mainWindow.lineEdit_server_ip.text()
    PORT = int(mainWindow.lineEdit_server_port.text())

def encode():
    stegoSamples = []
    
    # Get the cover file name from the line edit box
    coverFileName = mainWindow.lineEdit_cover.text()
    
    # Get the message file name from the line edit box
    messageFileName = mainWindow.lineEdit_message.text()
    
    # Get the stego file name to be saved to from the line edit box
    stegoFileName = mainWindow.lineEdit_stegopath.text()
    
    if(mainWindow.radioButton_DWT.isChecked()):
        
        # User must provide OBH, otherwise provide error box
        if (mainWindow.lineEdit_OBH.text() != ''):
            OBH = int(mainWindow.lineEdit_OBH.text())
            
        # Else embed the secret message    
        else:
            SS.showErrorMessage('Invalid OBH', 'Enter an integer')
            
    # Second method = Genetic Algorithm
    elif(mainWindow.radioButton_GA.isChecked()):
        # Get the string representation of the key in ASCII
        keyString = mainWindow.lineEdit_GA_key.text()
        
        # Convert ASCII to binary 
        binaryKey = fp.messageToBinary(keyString) 
        binaryKey = binaryKey * int((len(secretMessage) + float(len(secretMessage))/len(binaryKey)) )
        
    # If no encoding algorithm is selected, throw an erro message 
    else:
        SS.showErrorMessage("Invalid Encoding Algorithm selected",
                         "Select an encoding algorithm by selecting a radio button")    
        

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
    
    # Set the placeholder that will display the steganography file path selected
    mainWindow.lineEdit_stegopath.setPlaceholderText("Path")
    mainWindow.lineEdit_stegopath.setReadOnly(True)
    
    # Set the placeholder for the key of the GA
    mainWindow.lineEdit_GA_key.setPlaceholderText("Insert Key or browse for key file (.txt)")
    
    # Hide objects at start
    mainWindow.lineEdit_GA_key.hide()
    mainWindow.pushButton_browse_key.hide()
    mainWindow.lineEdit_LSB_nr.hide()
    mainWindow.label_type_receiver_IP.hide()
    mainWindow.lineEdit_receiver_IP.hide()
    
    # Connect the buttons to the appropriate slots
    mainWindow.pushButton_connect.clicked.connect(connectToServer)
    
    # Guide user to provide values 1, 2, 3 or 4
    mainWindow.lineEdit_OBH.setPlaceholderText("OBH")
    
    # Set the progress on the progress bars to 0 to start with
    mainWindow.progressBar_reading.setValue(0)
    mainWindow.progressBar_embedding.setValue(0)
    mainWindow.progressBar_writing.setValue(0)
    mainWindow.progressBar_message.setValue(0)
    
    # Set the GUI background to specified image
    mainWindow.setStyleSheet("QMainWindow {border-image: url(Media/music.jpg) 0 0 0 0 stretch stretch}")
    mainWindow.tabWidget.setStyleSheet("QWidget {background-color: grey }")
    # Execute and show the user interface
    mainWindow.show()
    app.exec()