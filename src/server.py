import socket
import sys
import _thread

HOST = ""
PORT = 9020

def threaded_client(conn):
    # get file name to download
    f = open("/home/johan/Desktop/file_received.pdf", "wb")
    while True:
        # get file bytes
        data = conn.recv(4096)
        if not data:
            break
        # write bytes on file
        f.write(data)
    f.close()
    print("[+] Download complete!")

    # close connection
    conn.close()
    print("[-] Client disconnected")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)

try:
    s.bind((HOST, PORT))
    
except socket.error as e:
    print(str(e))


s.listen(5)

print("Listening ...")

while (True):
    
    try:
        conn, addr = s.accept()
        
    except Exception:
        print("Socket timed out")
        conn.close()
        break
    
    print('[+] Client connected:', addr)
    start_new_thread(threaded_client, (conn,))
