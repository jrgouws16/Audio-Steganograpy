# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 20:47:42 2019

@author: Johan Gouws
"""
from PyQt5 import QtWidgets, uic
import socket
import threading
import sys
import sockets

clientThreads = []
serverThread = []
connections = []
addresses = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def threaded_client(conn):
    print("Thread")
    mainWindow.listWidget_log.addItem("Client thread created successfully")  
    while True:
        message = sockets.recv_one_message(conn)
        
        if (message == None):
              break
        
        elif (message.decode() == 'RECFILE'):
              mainWindow.listWidget_log.addItem("Server receiving file")
              f = open("Media/received.pdf", "wb")
              data = sockets.recv_one_message(conn)
              f.write(data)
              f.close()
              mainWindow.listWidget_log.addItem("Server receiving file success")
              
        elif (message.decode() == "Disconnect"):
              break
                            
        else:
              mainWindow.listWidget_log.addItem("Server receiving command")
              mainWindow.listWidget_log.addItem("Command -> " + message.decode())
    
    print("[-] Client disconnected")


def acceptClients(param):
      HOST = ""
      mainWindow.listWidget_log.addItem("Server listening thread created")
      global s
      global connections
      global addresses
      global clientThreads

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
              
              clientThreads.append(threading.Thread(target=threaded_client, args=(connections[-1],)))
              clientThreads[-1].isDaemon = True
              clientThreads[-1].start()
              
              print(addresses)
                
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
      
      mainWindow.label_server_status.setText("Server Status: Off")
      s.close()
      del addresses[:]
      del connections[:]
      del serverThread[:]
      print(addresses, connections, serverThread)


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
      
      
      
      
      
      
      
      
      
      