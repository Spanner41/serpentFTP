'''
Client Example Application

@author: Joseph Kostreva, Brady Steed
'''

import re
import socket
import string
import traceback
import paramiko
import os
import time

class Client:
    #used to connect to server
    hostname = None
    port = None
    transport = None
    
    #used to authenticate client identity on server
    accountName = None
    accountPass = None
    
    homedir = None
    storedFiles = []
    
    def loadConfig(self):
        if(os.path.isfile('config.txt')):
            config = open('config.txt', 'r')
            
            while 1:
                lines = config.readlines(5)
                if not lines:
                    break
                for line in lines:
                    words = re.split(' |\n', line)
                    
                    if words[0] == 'hostname': self.hostname = words[1]
                    if words[0] == 'port': self.port = int(words[1])
                    if words[0] == 'servername': self.servername = words[1]
                    if words[0] == 'password': self.hostname = words[1]
                    if words[0] == 'accountName': self.accountName = words[1]
                    if words[0] == 'accountPass': self.accountPass = words[1]
                    if words[0] == 'homedir': self.homedir = words[1]
                    
    def saveConfig(self):
        config = open('config.txt', 'wb')
        if self.hostname is not None:
            config.write('hostname ' + self.hostname)
            config.write(os.linesep)

        if self.port is not None:
            config.write('port ' + str(self.port))
            config.write(os.linesep)

        if self.accountName is not None:
            config.write('accountName ' + self.accountName)
            config.write(os.linesep)

        if self.accountPass is not None:
            config.write('accountPass ' + self.accountPass)
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

    #gather information for connection from command prompt
    def promptForConfig(self):
        if self.hostname is None:
            self.hostname = raw_input('hostname:')
        if self.port is None:
            self.port = int(raw_input('port:'))
        if self.accountName is None:
            self.accountName = raw_input('accountName:')
        if self.accountPass is None:
            self.accountPass = raw_input('accountPass:')
        if self.homedir is None:
            self.homedir = os.getcwd()
    
    #for future use in a GUI based implementation
    def setConnectionParameters(self, hostname=None, port=None, accountName=None, accountPass=None):
        self.hostname = hostname
        self.port = port
        self.accountName = accountName
        self.accountPass = accountPass
    
    #connect to sftp server
    def connect(self):
        try:
            self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.transport.connect((self.hostname, self.port))
            
            #self.transport = paramiko.Transport((self.hostname, 22))
            #self.transport.connect(username=self.servername, password=self.password)
            #self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        except Exception, e:
            print '*** Caught exception: %s: %s' % (e.__class__, e)
            traceback.print_exc()
            
    def disconnect(self):
        self.transport.send('disconnecting::')
        self.transport.close()
        
    #register user with server
    def register(self, hostname, accountName, accountPass):
        self.transport.send('register::' + hostname + "::" + accountName + '::' + accountPass)
        time.sleep(1)

    #send file list
    def sendFileList(self):
        self.transport.send('file list::' + str(len(self.storedFiles)) + '::')
        for name in self.storedFiles:
            self.transport.send('::' + name)
    
    #request file list
    def getFileList(self):
        self.transport.send('send file list::')

    #callback function of type function(int, int)
    def put(self, localpath, remotepath, callback=None):
        file_size = os.stat(localpath).st_size
        
        self.transport.send('putting::' + remotepath + '::' + str(file_size))


        readByte = open(localpath, "rb")
        data = readByte.read()
        readByte.close()

        self.transport.send(data)

    def get(self, remotepath, localpath):
        self.transport.send('getting::' + remotepath)

        file = open(localpath, 'wb')
        #receive the file
        bytes = self.transport.recv(1024)
        
        while(len(bytes) != 0):
            file.write(bytes)
            bytes = self.transport.recv(1024)
            if (len(bytes) < 1024):
                file.write(bytes)
                break
        file.close()
        
    def listen(self):
        commands = []
        bytes = ""
        while 1:
            bytes += self.transport.recv(1024)
            commands.extend(bytes.split('::'))
            
            if((not bytes.endswith('::')) and len(commands) > 0):
                bytes = commands.pop()
                
            if(len(commands) > 0):
                print(commands[0])
                
                if(commands[0] == 'send file list'):
                    self.sendFileList()
                    commands.pop(0)
                    
                if(commands[0] == 'file list' and len(commands) > 1 and len(commands) > commands[1] + 1):
                    commands.pop(0)
                    self.storedFiles = []
                    for i in range(int(commands[0])):
                        commands.pop(0)
                        self.storedFiles.append(commands[0])
                        
                if(commands[0] == 'getting'):
                    if(len(commands) > 1):
                        path = os.path.join(self.homedir, commands[1])
                        file = open(path, 'rb')
                        self.transport.send('putting::' + commands[1] + '::' + os.stat(path).st_size + '::')
                        buffer = file.read(1024)
                        while(len(buffer) != 0):
                            self.transport.send(buffer)
                            buffer = file.read(1024)
                        file.close()
                        commands.pop(0)
                        commands.pop(0)
                
                if(commands[0] == 'putting'):
                    if(len(commands) > 2):
                        commands.pop(0)
                        path = os.path.join(self.homedir, commands.pop(0))
                        file_size = commands.pop(0)
                        size = 0
                        file = open(path, 'wb')
                        if(len(commands) > 0):
                            buffer = commands.pop(0)
                        else:
                            buffer = bytes
                        file.write(buffer)
                        size += len(buffer)
                        while(file_size - size > 1024):
                                buffer = self.transport.recv(1024)
                                file.write(buffer)
                        buffer = self.transport.recv(file_size - size)
                        file.write(buffer)

client = Client()
client.loadConfig()
client.promptForConfig()
client.saveConfig()
client.connect()
client.register(client.hostname, client.accountName, client.accountPass)
client.put('folder.ico', 'folder1.ico')
time.sleep(2)
client.get('folder1.ico', 'folder2.ico')
#time.sleep(5)
#client.get('folder.ico', 'folder.ico')
#client.disconnect()
#client.listen()