import socket
from PyQt5 import QtWidgets, uic
import fileprocessing as fp
import SignalsAndSlots as SS
import time
 


'''
# Connect with the server
try:
      s.settimeout(1)
      s.connect((HOST, PORT))
      print("[+] Connected with Server")
      
      # get file name to send
      f_send = "Media/PDF_2.pdf"
      
      # open file
      with open(f_send, "rb") as f:
          # send file
          print("[+] Sending file...")
          data = f.read()
          s.send("Hello from Windows".encode())
          s.sendall(data)
          # close connection
          s.close()
          print("[-] Disconnected")
          f.close()
      
      
      s.close()    
      
'''


def encode():
      # Server to connect to
      HOST = mainWindow.lineEdit_server_ip.text()
      
      s = socket.socket(socket.AF_INET,   socket.SOCK_STREAM)
      # Port to connect to
      PORT = 9000
   
      # Connect with the server
      try:
            s.settimeout(1)
            s.connect((HOST, PORT))
            mainWindow.label_server_status.setText("Server Status: Connected")
                        
            s.send("Hell".encode())
            s.send("Seco".encode())
            
            s.send("COVR".encode())
            # get file name to send
            f_send = "Media/PDF_1.pdf"
            
            # open file
            with open(f_send, "rb") as f:
                # send file
                print("[+] Sending file...")
                data = f.read()
                s.sendall(data)
                f.close()
            time.sleep(1)
            s.send("DISK".encode())
            s.close()
            mainWindow.label_server_status.setText("Server Status: Disconnected")

            
      except Exception:
            SS.showErrorMessage("Connection Error", "Check whether host IP and port is correctly specified")

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
    mainWindow = uic.loadUi("ClientEncodingInterface.ui")
    
    # Set to connection family and SOCK_STREAM is for TCP connection
    s = socket.socket(socket.AF_INET,   socket.SOCK_STREAM)
    
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
    
    # Guide user to provide values 1, 2, 3 or 4
    mainWindow.lineEdit_LSB_nr.setPlaceholderText("LSB 1-4")
    
    # Connect the browse key to the setKey function
    mainWindow.pushButton_browse_key.clicked.connect(setKey)
    
    # Connect the encode pushbutton to the encode function when clicked
    mainWindow.pushButton_encode.clicked.connect(encode)
    
    # Connect the browse cover, message and stego file to slots
    mainWindow.pushButton_browse_cover.clicked.connect(setCoverPath)
    mainWindow.pushButton_browse_message.clicked.connect(setMessagePath)
    mainWindow.pushButton_browse_stego.clicked.connect(setStegoPath)
    
    # Set the progress on the progress bars to 0 to start with
    mainWindow.progressBar_reading.setValue(0)
    mainWindow.progressBar_embedding.setValue(0)
    mainWindow.progressBar_writing.setValue(0)
    mainWindow.progressBar_message.setValue(0)
    
    # Set the GUI background to specified image
    mainWindow.setStyleSheet("QMainWindow {border-image: url(Media/music.jpg) 0 0 0 0 stretch stretch}")
    
    # Execute and show the user interface
    mainWindow.show()
    app.exec()