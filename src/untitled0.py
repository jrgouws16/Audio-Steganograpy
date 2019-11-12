import AES

username = open('username.txt', 'w')
password = open('password.txt', 'w')
#
#print(AES.string2bits(AES.AESCipher('password').encrypt('password')))
#username.write(AES.string2bits(AES.AESCipher('username').encrypt('username')))
#password.write(AES.string2bits(AES.AESCipher('password').encrypt('password')))
#username.close()
#password.close()

print(AES.bits2string(AES.decryptBinaryString('11000111100101010100110101001011001010011101101010110010101111100010110001000110000001110100000100100101101001011101001001011101', 'username')))
a = ['a','b','c','d']
print(a.index('b'))