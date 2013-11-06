'''
Tracker Server Example App

@author: Joseph Kostreva, Brady Steed
'''

import traceback

import paramiko

import os

import time

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

class Connection:
    
    transport= None #ssh2 connection
    sftp= None #sftp client
    hostkeytype = None
    hostkey = None
    storedFiles = []
    _instance = None

    def __init__(self, hostname=None, username=None, password=None, size=1073741824):
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
    
    def getStoredFilesList(self, fileNameStored):
        for fileName in self.storedFiles:
            if fileName == fileNameStored:
                return fileName
            else:
                return None

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



import socket

hostname = '127.0.0.1'                 # Symbolic name meaning the local host
port = 9000              # Arbitrary non-privileged port
s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.bind((hostname, port))
s1.listen(1)
connection, address = s1.accept()
print 'Connected by', address

while True:
    data = connection.recv(1024)
    if not data: continue
    parsedData = data.split('::');
    if parsedData[0] == "register":
        tracker.addStorageLocation(parsedData[1], parsedData[2], parsedData[3])
        server = tracker.getAvailableStorageLocation()
        server.connect()
        break
while True:
    data = connection.recv(1024)
    if not data: continue
    parsedData = data.split('::');

    if parsedData[0] == "putting":
        
        file = open(parsedData[1], "wb")
        data = connection.recv(1024)
        while len(data) != 0:
            file.write(data)
            data = connection.recv(1024)
            if (len(data) < 1024):
                file.write(data)
                break
        file.close()

        server.put(parsedData[1], "/" + parsedData[1])

    elif parsedData[0] == "getting":
        server.get("/" + parsedData[1], parsedData[1])
        file_size = os.stat(parsedData[1]).st_size

        readByte = open(parsedData[1], "rb")
        data = readByte.read()
        readByte.close()

        connection.send(data)


connection.close()

#tracker.addStorageLocation("127.0.0.1", "user", "pass")

#server = tracker.getAvailableStorageLocation()
#server.connect()
# Send a file to the server
#server.put("folder.ico", "/folder.ico")

# Retrieve the file from the server
#if server.getStoredFilesList("folder.ico") != None:
#    server.get("/folder.ico", "folder.ico")
