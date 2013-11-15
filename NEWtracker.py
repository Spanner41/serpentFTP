import socket
import os
import random
import re

class Server():
    hostname = None
    port = None
    size = None
    sizeUsed = 0
    fileList = {}
    
    def __init__(self, hostname, port, size):
        self.hostname = hostname
        self.port = port
        self.size = size
        
class Client():
    hostname = None
    port = None
    fileList = []
    
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

class Tracker():
    
    servers = []
    clients = {}
    
    def __init__(self):
        pass
    
    def saveConfig(self):
        config = open('trackerconfig.txt', 'wb')
        config.write('servers ' + str(len(self.servers)) + os.linesep)
        for server in self.servers:
            config.write(server.hostname + ' ' + str(server.port) + ' ' +  str(server.size) + ' ' + str(server.fileList) + ' ' + str(len(server.fileList))+os.linesep)
            for name in server.fileList:
                config.write(name+' '+str(len(server.fileList[name])) + ' ' + server.fileList[name][0])
                for item in server.fileList[name][1:]:
                    config.write(' '+item)
                    
            config.write(os.linesep)
        config.write('clients ' + str(len(self.servers)) + os.linesep)
        for client in self.clients:
            config.write(client + ' ' + self.clients[client].hostname + ' ' + self.clients[client].port + ' ' + self.clients[client].fileList + ' ' + str(len(server.fileList)))
            for name in self.clients[client].fileList: config.write(' '+name)
            
    def loadConfig(self):
        if(os.path.isfile('trackerconfig.txt')):
            config = open('trackerconfig.txt', 'rb')
            while 1:
                line = config.readline()
                words = re.split(' |\n', line)
                
                if(words[0] == 'servers'):
                    line = config.readline()
                    names = re.split(' |\n', line)
                    for i in range(0,int(words[1])):
                        self.servers.append(Server(names[0], names[1], names[2]))
                        self.servers[i].fileList[names[3]]=[]
                        line = config.readline()
                        args = re.split(' |\n', line)
                        for j in int(names[4]):
                            self.servers[i].fileList[names[3]].append(args[j])
                        
            config.close()
    
    def addServer(self, hostname, port, size):
        self.servers.append(Server(hostname, port, size))
        
        for name in self.clients:
            self.servers[len(self.servers)-1].fileList[name]=[]
    
    def addClient(self, name, hostname, port):
        if not name in self.clients:
            self.clients[name] = Client(hostname, port)
            for server in self.servers:
                server.fileList[name]=[]
        else:
            self.clients[name].hostname = hostname
            self.clients[name].port = port
            
    def findClient(self, host, port):
        for client in self.clients:
            if self.clients[client].hostname == host and self.clients[client].port == port:
                return client
        
    def findFile(self, fileName, client):
        for server in self.servers:
            if client in server.fileList and fileName in server.fileList[client]:
                return server.hostname, server.port
        return None, None
            
    def findAvailableServer(self, size):
        number = random.randint(0, len(self.servers)-1)
        for i, server in enumerate(self.servers[number:]):
            if(server.size-server.sizeUsed >= size):
                return server.hostname, server.port, i
        for i, server in enumerate(self.servers[0:number]):
            if(server.size-server.sizeUsed >= size):
                return server.hostname, server.port, i
        return None, None, -1
    
    def updateSizeUsed(self, host, port, size):
        for server in self.servers:
            if server.hostname == host and server.port == port:
                server.sizeUsed = size
        
    def listen(self):
        host = ''
        port = 6001
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((host, port))
        
        while 1:
            data, addr = sock.recvfrom(1024)
            remotehost, remoteport = addr
            print 'from: ' + remotehost + ', ' + str(remoteport) + os.linesep + 'data: ' + data
            
            parsedData = data.split('::')
            
            if(parsedData[0] == 'addServer'):
                self.addServer(remotehost, int(parsedData[1]), int(parsedData[2]))
                
            if(parsedData[0] == 'updateSize'):
                self.updateSizeUsed(remotehost, remoteport, int(parsedData[1]))
                
            if(parsedData[0] == 'register'):
                self.addClient(parsedData[1], remotehost, remoteport)
            
            if(parsedData[0] == 'whereis'):
                serverhost, serverport = self.findFile(parsedData[1], self.findClient(remotehost, remoteport))
                sock.sendto('ack::'+ serverhost + '::' + str(serverport), addr)
                
            if(parsedData[0] == 'giveServer'):
                client = self.findClient(remotehost, remoteport)
                serverhost, serverport, index = self.findAvailableServer(int(parsedData[2]))
                sock.sendto('ack::'+ serverhost + '::' + str(serverport), addr)
                self.servers[index].fileList[client].append(parsedData[1])
                self.clients[client].fileList.append(parsedData[1])

tracker = Tracker()
#tracker.loadConfig()
tracker.listen()