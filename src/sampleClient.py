# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 20:47:41 2019

@author: Johan Gouws
"""
import socket
import struct

def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data.encode())

def send_one_file(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)

HOST = 'localhost'

s = socket.socket(socket.AF_INET,   socket.SOCK_STREAM)
# Port to connect to
PORT = 2000

try:
      s.connect((HOST, PORT))
      print("[+] Connected with Server")
      
      send_one_message(s, "My name is Johan")
      
      send_one_message(s, "RECFILE")
      
      f_send = "send.pdf"
      
      # open file
      with open(f_send, "rb") as f:
          print("[+] Sending file...")
          data = f.read()
          send_one_file(s, data)
          f.close()
      
     
      send_one_message(s, "My name is earl")
            
            
      s.close()

except Exception:
      print("Client Socket Error")
      s.close()