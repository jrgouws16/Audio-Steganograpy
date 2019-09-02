# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 20:47:42 2019

@author: Johan Gouws
"""
from PyQt5 import QtWidgets, uic
import SignalsAndSlots as SS
import socket
import struct
import threading
import sys

def recv_one_message(sock):
    lengthbuf = recvall(sock, 4)
    try:
          length = struct.unpack('!I', lengthbuf)
    except Exception:
          return None
    
    return recvall(sock, length[0])


def recvall(sock, count):

    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: 
              return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def threaded_client(conn):
    mainWindow.listWidget_log.addItem("Client thread created successfully")  
    while True:
        message = recv_one_message(conn)
        
        if (message == None):
              break
        
        elif (message.decode() == 'RECFILE'):
              mainWindow.listWidget_log.addItem("Server receiving file")
              f = open("Media/received.pdf", "wb")
              data = recv_one_message(conn)
              f.write(data)
              f.close()
              mainWindow.listWidget_log.addItem("Server receiving file success")
              
        elif (message.decode() == "Disconnect"):
              break
                            
        else:
              mainWindow.listWidget_log.addItem("Server receiving command")
              mainWindow.listWidget_log.addItem("Command -> " + message.decode())
            
    mainWindow.listWidget_log.addItem("Client", str(conn.getsockname()[0]), "Disconnecting")
    conn.close()
    mainWindow.listWidget_log.addItem("Client", str(conn.getsockname()[0]), "Disconnected successfully")
    
    print("[-] Client disconnected")


def startServer(param):
      HOST = ""
      mainWindow.listWidget_log.addItem("Server started")
      
      while (mainWindow.label_server_status.text() == "Server Status: On"):
          print("HI")
          try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind((HOST, int(mainWindow.lineEdit_port.text())))
                s.listen(5)
                
                try:
                      conn, addr = s.accept()
                      print("NOW here", conn, addr)
                      mainWindow.listWidget_log.addItem("Client " + str(addr) + " connected on port " + mainWindow.lineEdit_port.text())
                      threaded_client(conn)
                      
                except Exception:
                      s.close()
            
          except Exception:
                SS.showErrorMessage("Error opening port.", "Check if port provided is valid.")
                
      mainWindow.listWidget_log.addItem("Server ended")      
        
def startServerThread():
      x = threading.Thread(target=startServer, args=(1,))
      mainWindow.label_server_status.setText("Server Status: On")
      x.start()
      return x
            
def endServer():
      mainWindow.label_server_status.setText("Server Status: Off")


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
    sys.exit(app.exec_())
      
      
      
      
      
      
      
      
      
      