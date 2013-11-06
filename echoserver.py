import socket
import threading

def listen(client):
    while 1:
        try:
            client.send(raw_input())
        except Exception, e:
            exit()

host = '' 
port = 50000 
backlog = 5 
size = 1024 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind((host,port))
s.listen(backlog)

client, address = s.accept()
client.settimeout(3.0)
sendthread = threading.Thread(target=listen, args = (client, ))
sendthread.start()

while threading.activeCount():
    try:
        data = client.recv(size)
        print("received: " + data)
    except socket.timeout:
        pass
    except:
        exit()

client.close()
s.close()