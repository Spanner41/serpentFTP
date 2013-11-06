'''
Tracker Client Example App

@author: Joseph Kostreva, Brady Steed
'''

import socket

hostname = '127.0.0.1'    # The remote host
port = 8000             # The same port as used by the server
s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.connect((hostname, port))
s1.send('Reg::127.0.0.1::username::password::10000::10000')
data = s1.recv(1024)
s1.send('Send::folder.ico')
data = s1.recv(1024)
s1.send('Retrieve::folder.ico')
data = s1.recv(1024)
s1.close()
print 'Received', repr(data)

# Brady's Code for Client class will replace this here...