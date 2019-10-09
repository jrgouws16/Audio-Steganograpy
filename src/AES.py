# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 23:18:51 2019

@author: Johan Gouws
"""
#!/usr/bin/env python3
#
# This is a simple script to encrypt a message using AES
# with CBC mode in Python 3.
# Before running it, you must install pycryptodome:
#
# $ python -m pip install PyCryptodome
#
# Author.: José Lopes
# Date...: 2019-06-14
# License: MIT
##

from hashlib import md5
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import numpy as np

def bits2string(b=None):
    return ''.join([chr(int(b[x:x+8], 2)) for x in range(0, len(b), 8)])
def bitstring_to_bytes(s):
    return int(s, 2).to_bytes(len(s) // 8, byteorder='big')
def string2bits(s=''):
    return "".join([bin(ord(x))[2:].zfill(8) for x in s])


class AESCipher:
    
    def __init__(self, key):
        self.key = ''
        for i in (md5(key.encode('utf8')).digest()):
              self.key += bits2string(np.binary_repr(i,8))
        self.key = string2bits(self.key)
        self.key = bitstring_to_bytes(self.key)
        self.cipher = None  

    def encrypt(self, plainText):
          plainText = plainText.encode()
          self.cipher = AES.new(self.key, AES.MODE_CBC, b'\xa0\x9e([\x0f\x17\x0f\x11iG\x0b{\xc7\xf2\x91\xfd')
          
          encrypted_bytes = self.cipher.encrypt(pad(plainText, AES.block_size))
                      
          total = ""
          for i in encrypted_bytes:
              total += np.binary_repr(i,8)
            
          encrypted = bits2string(total)
          return encrypted

    def decrypt(self, encrypted):
          
          
            
          
          encrypted = string2bits(encrypted)
          encrypted = bitstring_to_bytes(encrypted)
            
          iv = b'\xa0\x9e([\x0f\x17\x0f\x11iG\x0b{\xc7\xf2\x91\xfd' 
          try:
               cipher = AES.new(self.key, AES.MODE_CBC, iv)
               pt = unpad(cipher.decrypt(encrypted), AES.block_size)
               return pt.decode()
          except Exception:
               return "WRONG_KEY"


def encryptBinaryString(binaryString, key):
    plainText = bits2string(binaryString)
    encrypted = AESCipher(key).encrypt(plainText)
    binaryEncrypted = string2bits(encrypted)
    
    return binaryEncrypted

def decryptBinaryString(binaryString, key):
    
    encrypted = bits2string(binaryString)
    
    decrypted = AESCipher(key).decrypt(encrypted)
    binaryDecrypted = string2bits(decrypted)
    return binaryDecrypted

