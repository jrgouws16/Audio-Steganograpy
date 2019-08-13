import socket


HOST = "localhost"
PORT = 9999

s = socket.socket(socket.AF_INET,   socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("[+] Connected with Server")

# get file name to send
f_send = "PDF_3.pdf"
# open file
with open(f_send, "rb") as f:
    # send file
    print("[+] Sending file...")
    data = f.read()
    s.sendall(data)

    # close connection
    s.close()
    print("[-] Disconnected")
    f.close()