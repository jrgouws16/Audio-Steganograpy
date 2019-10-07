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
from base64 import b64decode
from base64 import b64encode

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

def string2bits(s=''):
    return "".join([bin(ord(x))[2:].zfill(8) for x in s])

def bits2string(b=None):
    return ''.join([chr(int(b[x:x+8], 2)) for x in range(0, len(b), 8)])


class AESCipher:
    def __init__(self, key):
        self.key = md5(key.encode('utf8')).digest()

    def encrypt(self, data):
        iv = get_random_bytes(AES.block_size)
        self.cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return b64encode(iv + self.cipher.encrypt(pad(data.encode('utf-8'), 
            AES.block_size)))

    def decrypt(self, data):
        raw = b64decode(data)
        self.cipher = AES.new(self.key, AES.MODE_CBC, raw[:AES.block_size])
        return unpad(self.cipher.decrypt(raw[AES.block_size:]), AES.block_size)

def encryptBinaryString(binaryString, key):
    
  
    plainText = bits2string(binaryString)
    encrypted = AESCipher(key).encrypt(plainText).decode('utf-8')
    binaryEncrypted = string2bits(encrypted)
    
    return binaryEncrypted

def decryptBinaryString(binaryString, key):
    
    encrypted = bits2string(binaryString)
    
    decrypted = AESCipher(key).decrypt(encrypted).decode('utf-8')
    binaryDecrypted = string2bits(decrypted)
    return binaryDecrypted

if __name__ == '__main__':
    print('TESTING ENCRYPTION')
    msg       = "This is AES encryption testing. If you can read this after decoding, it was succesfully encoded and decoded."
    pwd       = "123456789"
    message = string2bits(msg)
    print(len(message))
    encrypted = encryptBinaryString(message, pwd)
    print(len(encrypted))
    #print("Ciphertext...:", text_from_bits(encrypted))
    pwd = "123456789"
    print("TESTING DECRYPTION")
    extractMessage = decryptBinaryString(encrypted, pwd)
    print("Message...:", bits2string(extractMessage))
    if (msg!=bits2string(extractMessage)):
          print("Unsuccessful")
          
    else:
          print("Successful")