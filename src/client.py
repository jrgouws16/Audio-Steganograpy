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

server = []

'''

  
f_send = "Media/send.pdf"
  
# open file
with open(f_send, "rb") as f:
    print("[+] Sending file...")
    data = f.read()
    sockets.send_one_file(server[0], data)
    f.close()

'''

def sendMessageToServer(message):
    try:
        sockets.send_one_message(server[0], message)
      
    except Exception:
          SS.showErrorMessage("Connection Error", "Cannot communicate with the server")
          server[0].close()
          del server[:]
          mainWindow.label_server_status.setText("Status: Disonnected")
          
def sendFileToServer(filePath):
    try:
        with open(filePath, "rb") as f:
            data = f.read()
            
    except:
        SS.showErrorMessage("File error.", filePath + " does not exist.")
    
    try:
        sockets.send_one_file(server[0], data)
        f.close() 
            
    except Exception:
          SS.showErrorMessage("Connection Error", "Cannot communicate with the server")
          server[0].close()
          del server[:]
          mainWindow.label_server_status.setText("Status: Disonnected")

def connectToServer():
    global server
    
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
           
        except Exception:
              SS.showErrorMessage("Error Connecting", "Server unavailable.")
              s.close()
              del server[:]
     
def disconnectFromServer():
    sendMessageToServer("Disconnect")
    server[-1].close()
    del server[:]
    mainWindow.label_server_status.setText("Status: Disonnected")


def encode():
    # Get the cover file name from the line edit box
    coverFileName = mainWindow.lineEdit_cover.text()
    sendMessageToServer(coverFileName)
    
    # Get the message file name from the line edit box
    messageFileName = mainWindow.lineEdit_message.text()
    sendMessageToServer(messageFileName)
    
    # Get the stego file name to be saved to from the line edit box
    stegoFileName = mainWindow.lineEdit_stegopath.text()
    sendMessageToServer(stegoFileName)
    
    if(mainWindow.radioButton_DWT.isChecked()):
        sendMessageToServer("DWT selected")
        
        # User must provide OBH, otherwise provide error box
        if (mainWindow.lineEdit_OBH.text() != ''):
            OBH = int(mainWindow.lineEdit_OBH.text())
            sendMessageToServer("OBH of "+ str(OBH) + " selected.")
            
        # Else embed the secret message    
        else:
            SS.showErrorMessage('Invalid OBH', 'Enter an integer')
            
    # Second method = Genetic Algorithm
    elif(mainWindow.radioButton_GA.isChecked()):
        # Get the string representation of the key in ASCII
        keyString = mainWindow.lineEdit_GA_key.text()
        sendMessageToServer("GA selected")
        sendMessageToServer("Key is "+ keyString)
        # Convert ASCII to binary 
        # binaryKey = fp.messageToBinary(keyString) 
        # binaryKey = binaryKey * int((len(secretMessage) + float(len(secretMessage))/len(binaryKey)) )
        
    # If no encoding algorithm is selected, throw an erro message 
    else:
        SS.showErrorMessage("Invalid Encoding Algorithm selected",
                         "Select an encoding algorithm by selecting a radio button")    
        
   
def setCoverPath():
      mainWindow.lineEdit_cover.setText(fp.openFile())
      
def setMessagePath():
      mainWindow.lineEdit_message.setText(fp.openFile())
      
def setStegoPath():
      mainWindow.lineEdit_stegopath.setText(fp.saveFile())
      
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
    
    # Set the placeholder that will display the steganography file path selected
    mainWindow.lineEdit_stegopath.setPlaceholderText("Path")
    mainWindow.lineEdit_stegopath.setReadOnly(True)
    
    # Set the placeholder for the key of the GA
    mainWindow.lineEdit_GA_key.setPlaceholderText("Insert Key or browse for key file (.txt)")
    
    # Hide objects at start
    mainWindow.lineEdit_GA_key.hide()
    mainWindow.pushButton_browse_key.hide()
    mainWindow.lineEdit_OBH.hide()
    mainWindow.label_type_receiver_IP.hide()
    mainWindow.lineEdit_receiver_IP.hide()
    
    # Connect the buttons to the appropriate slots
    mainWindow.pushButton_connect.clicked.connect(connectToServer)
    mainWindow.pushButton_encode.clicked.connect(encode)
    mainWindow.pushButton_browse_key.clicked.connect(setKey)
    mainWindow.pushButton_browse_cover.clicked.connect(setCoverPath)
    mainWindow.pushButton_browse_message.clicked.connect(setMessagePath)
    mainWindow.pushButton_browse_stego.clicked.connect(setStegoPath)
    mainWindow.pushButton_disconnect.clicked.connect(disconnectFromServer)
    
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