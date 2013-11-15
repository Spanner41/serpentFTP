import os
import re
import socket

class Client():
    
    #server info
    hostname = None
    port = None
    sock = None
    accountName = None
    homedir = None
    storedFiles = []
    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def loadConfig(self):
        if(os.path.isfile('clientconfig.txt')):
            config = open('clientconfig.txt', 'rb')
            
            while 1:
                lines = config.readlines(5)
                if not lines:
                    break
                for line in lines:
                    words = re.split(' |'+os.linesep, line)
                    
                    if words[0] == 'hostname': self.hostname = words[1]
                    if words[0] == 'port': self.port = int(words[1])
                    if words[0] == 'accountName': self.accountName = words[1]
                    if words[0] == 'homedir': self.homedir = words[1]
                    if words[0] == 'storedFiles':
                        for i in range(0,int(words[1])):
                            self.storedFiles.append(words[i + 2])
            config.close()
            self.promptForConfig()

    def promptForConfig(self):
        if self.hostname is None:
            self.hostname = raw_input('hostname:')
        if self.port is None:
            self.port = int(raw_input('port:'))
        if self.accountName is None:
            self.accountName = raw_input('accountName:')
        if self.homedir is None:
            self.homedir = os.getcwd()
            
    def saveConfig(self):
        config = open('clientconfig.txt', 'wb')
        if self.hostname is not None:
            config.write('hostname ' + self.hostname)
            config.write(os.linesep)

        if self.port is not None:
            config.write('port ' + str(self.port))
            config.write(os.linesep)

        if self.accountName is not None:
            config.write('accountName ' + self.accountName)
            config.write(os.linesep)

        if self.homedir is not None:
            config.write('homedir ' + self.homedir)
            config.write(os.linesep)
            
        if self.storedFiles is not []:
            config.write('storedFiles ' + str(len(self.storedFiles)))
            for name in self.storedFiles:
                config.write(' ' + name)
            config.write(os.linesep)

        config.close()
            
    def disconnect(self):
        self.sock.close()
        
    def register(self):
        self.sock.sendto('register::' + self.accountName, (self.hostname, self.port))
        
    def getFileList(self):
        return self.storedFiles
        
    def get(self, filename):
        self.sock.sendto('whereis::'+filename, (self.hostname, self.port))
        data, addr = self.sock.recvfrom(1024)
        parsedData = data.split('::')
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((parsedData[1], int(parsedData[2])))
        server.send('request::'+filename)
        
        f = open(filename, 'wb')
        
        #receive the file
        data = server.recv(1024)

        while len(data) != 0:
            f.write(data)
            data = server.recv(1024)
            if (len(data) < 1024):
                f.write(data)
                break
            
        f.close()
        server.close()
        
    def put(self, filename):
        file_size = os.stat(filename).st_size
        self.sock.sendto('giveServer::' + filename + '::' + str(file_size), (self.hostname, self.port))
        data, addr = self.sock.recvfrom(1024)
        parsedData = data.split('::')
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((parsedData[1], int(parsedData[2])))
        server.send('take::'+filename)
        
        readByte = open(filename, "rb")
        data = readByte.read()
        readByte.close()

        server.send(data)
        server.close()
        self.storedFiles.append(filename)
        
client = Client()
client.loadConfig()
client.promptForConfig()
client.saveConfig()
client.register()

client.put('folder.ico')
client.get('folder.ico')