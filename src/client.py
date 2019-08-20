import socket


HOST = "192.168.0.8"
PORT = 9020

s = socket.socket(socket.AF_INET,   socket.SOCK_STREAM)

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

