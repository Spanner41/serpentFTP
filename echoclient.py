import socket
import threading

def listen(client):
    while 1:
        try:
            client.send(raw_input())
            
        except Exception, e:
            exit()

host = '127.0.0.1' 
port = 50000
size = 1024 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.settimeout(3.0)
s.connect((host, port))

sendthread = threading.Thread(target=listen, args = (s, ))
sendthread.start()

while threading.activeCount() > 1:
    try:
        data = s.recv(size)
        print("received: " + data)
    except socket.timeout:
        pass
    except:
        exit()
        
s.close()