'''
Tracker Server Example App

@author: Joseph Kostreva, Brady Steed
'''

import traceback
import paramiko
import os
import re
import socket

from multiprocessing import Process

def Singleton(singleClass):
    if not singleClass._instance:
        singleClass._instance = singleClass()
    return singleClass._instance

class Tracker:
    _instance = None

    def __init__(self):
        self.connectionList = []

    def addStorageLocation(self, hostnameValue, usernameValue, passwordValue):
        server = Connection()
        server.setConnectionParameters(hostname=hostnameValue,username=usernameValue,password=passwordValue)
        self.connectionList.append(server)

    def getAvailableStorageLocation(self):
        if (self.connectionList == None):
            return None
        else:
            for connection in self.connectionList:
                if connection.getRemainingSize() != 0:
                    return connection
            return None
        
    def getConnection(self, hostname):
        if (self.connectionList == None):
            return None
        
        for connection in self.connectionList:
            if connection.hostname == hostname:
                return connection

class Connection:
    
    transport= None #ssh2 connection
    sftp= None #sftp client
    hostkeytype = None
    hostkey = None
    _instance = None

    def __init__(self, hostname=None, username=None, password=None, size=100000):
        
        self.storedFiles = ["test1.txt", "test2.txt", "test3.txt"]
        self.hostname = hostname
        self.username = username
        self.password = password
        self.remainingSize = size

        self.bDownFlag = False
        self.mouseFocusFlag = False
        self.bUpFlag = False
        
        self.bDownFlagServer = False
        self.mouseFocusFlagServer = False
        self.bUpFlagServer = False
    
    def getStoredFilesArray(self):
        return self.storedFiles
    
    def getStoredFilesList(self, fileNameStored):
        for fileName in self.storedFiles:
            if fileName == fileNameStored:
                return fileName
            else:
                return None
            
    def loadFileList(self):
        if(os.path.isfile(self.username + '_' + self.hostname + '_fileList.txt')):
            config = open(self.username + '_' + self.hostname + '_fileList.txt', 'r')
            
            while 1:
                lines = config.readlines(5)
                if not lines:
                    break
                for line in lines:
                    words = re.split(' |\n', line)
                    
                    if words[0] == 'storedFiles':
                        for word in words[2:]:
                            self.storedFiles.append(word)
                            self.storedFiles = list(set(self.storedFiles))
            config.close()

    def saveFileList(self):
        config = open(self.username + '_' + self.hostname + '_fileList.txt', 'wb')
        
        if self.storedFiles is not []:
            config.write('storedFiles ' + str(len(self.storedFiles)))
            for name in self.storedFiles:
                config.write(' ' + name)
            config.write(os.linesep)

        config.close()

    def getRemainingSize(self):
        return self.remainingSize
    
    def setRemainingSize(self, size):
        self.remainingSize = size
        
    def setConnectionParameters(self, hostname=None, username=None, password=None):
        self.hostname = hostname
        self.username = username
        self.password = password

    def getTransport(self):
        if self.transport is None:
            self.transport = paramiko.Transport((self.hostname, 22))
        return self.transport
    
    def getCwd(self):
        sftp = self.getSFTP()
        if sftp.getcwd() == None:
            sftp.chdir("/")
        return sftp.getcwd()
    
    def getListDir(self):
        sftp = self.getSFTP()
        return sftp.listdir()
    
    def chDir(self, dirPath):
        sftp = self.getSFTP()
        sftp.chdir(dirPath)
        
    def getSFTP(self):
        if self.transport is not None and self.sftp is None:
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        return self.sftp
    
    def validate(self):
        pass
    
    def connect(self):
        
        self.validate()
        self.getTransport()
        
        if self.transport is not None:
            self.transport.connect(username=self.username, password=self.password)
          
    #send a file of name "filename"
    def put(self, filepath, localpath, callback=None):

        sftp = self.getSFTP()

        try:
            self.storedFiles.append(filepath)
            self.setRemainingSize(self.getRemainingSize() - os.path.getsize(filepath))
            sftp.put(filepath, localpath, callback)

        except Exception, e:
            print '*** Caught exception: %s: %s' % (e.__class__, e)
            traceback.print_exc()

    #retrieve a file of name filename
    def get(self, filepath, localpath, callback=None):

        sftp = self.getSFTP()

        sftp.get(filepath, localpath, callback)
        try:
            sftp.get(filepath, localpath)
            
        except Exception, e:
            print '*** Caught exception: %s: %s' % (e.__class__, e)
            traceback.print_exc()
            
    def close(self):
        self.transfer.close()

tracker = Singleton(Tracker)

def handler():
    hostname = '' # local host 
    port = 9007 # Arbitrary non-privileged port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((hostname, port))
    server.listen(1)
    connection, addr = server.accept()
    while True:
        data = connection.recv(1024)
        if not data: continue
        parsedData = data.split('::')

        if parsedData[0] == "register":
            tracker.addStorageLocation(parsedData[1], parsedData[2], parsedData[3])
            server = tracker.getAvailableStorageLocation()
            server.connect()
            server.loadFileList()
            break

    while True:
        data = connection.recv(1024)
        if not data: continue
        parsedData = data.split('::')
    
        if parsedData[0] == "putting":
            file = open(parsedData[1], "wb")
            data = connection.recv(1024)
            while len(data) != 0:
                if data.find("MARKERPUT") == -1:
                    pass
                else:
                    data = data.replace("MARKERPUT", "")
                    file.write(data)
                    break
                file.write(data)
                data = connection.recv(1024)

            file.close()

            server.put(parsedData[1], "/" + parsedData[1])

            server.saveFileList()
        elif parsedData[0] == "getting":
            server.get(parsedData[1], parsedData[2])

            readByte = open(parsedData[1].replace("/", ""), "rb")
            data = readByte.read()
            readByte.close()

            data = data + "MARKERGET"
            connection.send(data)

            server.loadFileList()
        elif parsedData[0] == "sendfilelist":
            lines = server.getStoredFilesArray()
            concatLine = ""
            for line in lines:
                if isinstance(line, str):
                    if line != "":
                        concatLine = concatLine + line + "::"
            concatLine = concatLine + "MARKERFILELIST"
            connection.sendall(concatLine)
    connection.close()

if __name__ == '__main__':
    for i in range(1,3): # Create 2 processes
        p = Process(target=handler, args=())
        p.start()
