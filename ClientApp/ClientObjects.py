import base64
import getpass
import os
import socket
import sys
import traceback

import paramiko

#Connection object controls an ssh2 connection and provides basic sftp functionality
class Connection(object):
    
    transport= None #ssh2 connection
    sftp= None #sftp client
    hostkeytype = None
    hostkey = None
    
    def __init__(self, hostname=None, username=None, password=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        
    def getTransport(self):
        
        if self.transport is None:
            self.transport = paramiko.Transport((self.hostname, 22))
        return self.transport
    
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
    def send(self, filename):
        
        sftp = getSFTP()
        
        try:
            data = open(file, 'rb').read()
            sftp.open(file, 'wb').write(data)
            
        except Exception, e:
            print '*** Caught exception: %s: %s' % (e.__class__, e)
            traceback.print_exc()
            try:
                self.close()
            except:
                pass
                
    #retrieve a file of name filename
    def retrieve(self, filename):
        
        sftp = getSFTP()
        
        try:
            data = sftp.open(file, 'rb').read()
            open(file, 'wb').write(data)
            
        except Exception, e:
            print '*** Caught exception: %s: %s' % (e.__class__, e)
            traceback.print_exc()
            
    def close(self):
        self.transfer.close()