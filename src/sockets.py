# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 13:34:44 2019

@author: project
"""
import struct

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

def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data.encode())

def send_one_file(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)