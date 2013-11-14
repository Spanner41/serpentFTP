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
    storedFiles = ['folder.ico', 'echoserver.py']
    _instance = None
    
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
            
        except Exception, e:
            print '*** Caught exception: %s: %s' % (e.__class__, e)
            traceback.print_exc()
            
    def disconnect(self):
        self.transport.close()
        
    #register user with server
    def register(self, hostname, accountName, accountPass):
        self.transport.send('register::' + hostname + "::" + accountName + '::' + accountPass )
        #time.sleep(1)

    #send file list
    def sendFileList(self):
        buffer = 'file list::' + str(len(self.storedFiles)) + '::[' + self.storedFiles[0]
        
        for name in self.storedFiles[1:]:
            buffer += ',' + name
        
        self.transport.send(buffer + ']')
    
    #request file list
    def getFileList(self):
        self.transport.send("sendfilelist::myfile.txt")
        fileList = ""
        fileListArray = []
        data = self.transport.recv(1024)
        while len(data) != 0:
            fileList = fileList + data
            data = self.transport.recv(1024)
            if (len(data) < 1024):
                fileList = fileList + data
                break
        fileListArray = fileList.split("::")
        fileListArray.pop(len(fileListArray)-1)
        return fileListArray

    #callback function of type function(int, int)
    def put(self, localpath, remotepath, callback=None):
        file_size = os.stat(localpath).st_size
        
        self.transport.send('putting::' + remotepath)

        readByte = open(localpath, "rb")
        data = readByte.read()
        readByte.close()

        self.transport.send(data)

    def get(self, remotepath, localpath):
        print remotepath
        print localpath
        self.transport.send('getting::' + remotepath + "::" + localpath)

        file = open(localpath, 'wb')
        
        #receive the file
        data = self.transport.recv(1024)

        while len(data) != 0:
            file.write(data)
            data = self.transport.recv(1024)
            if (len(data) < 1024):
                file.write(data)
                break
        file.close()
        
        self.storedFiles.append(remotepath)
