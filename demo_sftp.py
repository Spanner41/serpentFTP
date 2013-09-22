import base64
import getpass
import os
import socket
import sys
import traceback

import paramiko

def transfer(): 
    try:
        t = paramiko.Transport((hostname, port))
        t.connect(username=username, password=password, hostkey=hostkey)
        sftp = paramiko.SFTPClient.from_transport(t)

        # Prompt for type of transfer
        mode = ''
        while mode != 'r' and mode != 'R' and mode != 's' and mode != 'S':
            mode = raw_input('send or retrieve (s/r):')
        
	    # Send file to server
        if mode == 's' or mode == 'S':
            send(sftp)

        # Retrieve file from server
        if mode == 'r' or mode == 'R':
            retrieve(sftp)
            
        t.close()

    except Exception, e:
        print '*** Caught exception: %s: %s' % (e.__class__, e)
        traceback.print_exc()
        try:
            t.close()
        except:
            pass
            
def send(sftp):
    try:
        files = [f for f in os.listdir('.') if os.path.isfile(f) and f[0] != '.']
        for names in files:
            print '%s' % names

        file = raw_input('filename: ')

        data = open(file, 'rb').read()
        sftp.open(file, 'wb').write(data)
        
    except Exception, e:
        print '*** Caught exception: %s: %s' % (e.__class__, e)
        traceback.print_exc()
        try:
            t.close()
        except:
            pass
            
def retrieve(sftp):
    try:
        files = [f for f in sftp.listdir(path='.')]
        for names in files:
            print '%s' % names

        file = raw_input('filename: ')
        
        data = sftp.open(file, 'rb').read()
        open(file, 'wb').write(data)
        
    except Exception, e:
        print '*** Caught exception: %s: %s' % (e.__class__, e)
        traceback.print_exc()
        
# setup logging
paramiko.util.log_to_file('demo_sftp.log')

# get hostname
username = ''
if len(sys.argv) > 1:
    hostname = sys.argv[1]
    if hostname.find('@') >= 0:
        username, hostname = hostname.split('@')
else:
    hostname = raw_input('Hostname: ')
if len(hostname) == 0:
    print '*** Hostname required.'
    sys.exit(1)
port = 22
if hostname.find(':') >= 0:
    hostname, portstr = hostname.split(':')
    port = int(portstr)

# get username
if username == '':
    default_username = getpass.getuser()
    username = raw_input('Username [%s]: ' % default_username)
    if len(username) == 0:
        username = default_username
password = getpass.getpass('Password for %s@%s: ' % (username, hostname))

# get host key, if we know one
hostkeytype = None
hostkey = None
try:
    host_keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
except IOError:
    try:
        # try ~/ssh/ too, because windows can't have a folder named ~/.ssh/
        host_keys = paramiko.util.load_host_keys(os.path.expanduser('~/ssh/known_hosts'))
    except IOError:
        print '*** Unable to open host keys file'
        host_keys = {}

if host_keys.has_key(hostname):
    hostkeytype = host_keys[hostname].keys()[0]
    hostkey = host_keys[hostname][hostkeytype]
    print 'Using host key of type %s' % hostkeytype


# now, connect and use paramiko Transport to negotiate SSH2 across the connection
try:
	transfer()

except Exception, e:
    print '*** Caught exception: %s: %s' % (e.__class__, e)
    traceback.print_exc()
    try:
        t.close()
    except:
        pass
    sys.exit(1)