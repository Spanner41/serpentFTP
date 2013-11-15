import socket
import os
import re


class Server():
    trackerhostname = None
    trackerport = None
    hostname = None
    port = None
    fileList = []
    size = None
    sizeUsed = 0
    sock = None
    
    def __init__(self, size):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.size = size
        self.hostname = '' # local host 
        self.port = 9007 # Arbitrary non-privileged port
        self.trackerhostname = '127.0.0.1'
        self.trackerport = 6001
        
    def loadConfig(self):
        if(os.path.isfile('serverconfig.txt')):
            config = open('serverconfig.txt', 'rb')
            
            while 1:
                lines = config.readlines(5)
                if not lines:
                    break
                for line in lines:
                    words = re.split(' |\n', line)
                    
                    if words[0] == 'fileList':
                        for i in words[1]:
                            self.storedFiles.append(words[i + 2])
            config.close()
            
    def saveConfig(self):
        config = open('serverconfig.txt', 'wb')
        if self.port is not None:
            config.write('port ' + self.port)
            config.write(os.linesep)
        if self.trackerhostname is not None:
            config.write('trackerhostname ' + self.trackerhostname)
            config.write(os.linesep)
        if self.trackerport is not None:
            config.write('trackerport ' + self.trackerport)
            config.write(os.linesep)
        if self.size is not None:
            config.write('size ' + self.size)
            config.write(os.linesep)
        if self.fileList is not []:
            config.write('fileList ' + str(len(self.fileList)))
            for name in self.fileList:
                config.write(' ' + name)
        config.close()
        
    def promptForConfig(self):
        if self.port is None:
            self.port = raw_input('port:')
        if self.trackerhostname is None:
            self.trackerhostname = int(raw_input('trackerhostname:'))
        if self.trackerport is None:
            self.trackerport = raw_input('trackerport:')
        if self.homedir is None:
            self.homedir = os.getcwd()
    
    def register(self):
        self.sock.sendto('addServer::' + str(self.port) + '::' + str(self.size), (self.trackerhostname, self.trackerport))
        
    def updateSizeUsed(self):
        size = 0
        for f in self.fileList:
            size += os.stat(f).st_size
        self.sizeUsed = size
        
        self.sock.sendto('updateSize::' + str(self.sizeUsed), (self.trackerhostname, self.trackerport))
    
    def listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.hostname, self.port))
        server.listen(5)
        
        while 1:
            connection, addr = server.accept()
            
            data =connection.recv(1024)
            parsedData = data.split('::')
            
            if(parsedData[0] == 'request'):
                readByte = open('1' + parsedData[1], "rb")
                data = readByte.read()
                readByte.close()
                connection.send(data)
            
            if(parsedData[0] == 'take'):
                f = open('/1' + parsedData[1], 'wb')
        
                #receive the file
                data = connection.recv(1024)
                while len(data) != 0:
                    f.write(data)
                    data = connection.recv(1024)
                    if (len(data) < 1024):
                        f.write(data)
                        break
                f.close()
                self.updateSizeUsed()
                
            connection.close()
    
    #write a function to migrate files off of server
    
server = Server(4194304)
server.register()
server.listen()