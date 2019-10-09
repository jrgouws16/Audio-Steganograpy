from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import numpy as np

def bits2string(b=None):
    return ''.join([chr(int(b[x:x+8], 2)) for x in range(0, len(b), 8)])
def bitstring_to_bytes(s):
    return int(s, 2).to_bytes(len(s) // 8, byteorder='big')
def string2bits(s=''):
    return "".join([bin(ord(x))[2:].zfill(8) for x in s])


plainText = "hello"

data = plainText.encode()

key = get_random_bytes(16)
cipher = AES.new(key, AES.MODE_CBC)
ct_bytes = cipher.encrypt(pad(data, AES.block_size))

total = ""
for i in ct_bytes:
    total+=np.binary_repr(i,8)

myCipher = bits2string(total)

print("CipherText = ", myCipher)

myCipher = string2bits(myCipher)
myCipher = bitstring_to_bytes(myCipher)

iv = cipher.iv 

try:
     ct = myCipher
     
     cipher = AES.new(key, AES.MODE_CBC, iv)
     pt = unpad(cipher.decrypt(ct), AES.block_size)
     print("The message was: ", pt)
except Exception:
     print("Incorrect decryption")
