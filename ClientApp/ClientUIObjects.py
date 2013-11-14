'''
Client UI Objects

@author: Joseph Kostreva, Brady Steed
'''
from ClientObjects import Connection
from ClientObjects import Singleton
from ClientExample import Client
from Tkinter import *
import ttk
import glob
import os
import time

class StatusBar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)

    def set(self, formating, *args):
        self.label.config(text=formating % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()
        
#class that creates a dialog window
class ConnectDialog(Toplevel):
    
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.transient(master) #hides window from task bar
        self.title('Connect')
        self.master = master
        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (master.winfo_rootx()+50,
                                  master.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)


    def body(self, master):
        Label(master, text="Host:").grid(row=0)
        Label(master, text="Username:").grid(row=1)
        Label(master, text="Password:").grid(row=2)

        self.hostEntry = Entry(master)
        self.usernameEntry = Entry(master)
        self.passwordEntry = Entry(master, show="*")

        self.hostEntry.grid(row=0, column=1)
        self.usernameEntry.grid(row=1, column=1)
        self.passwordEntry.grid(row=2, column=1)
        return self.hostEntry # initial focus

    def buttonbox(self):
        box = Frame(self)

        w = Button(box, text="Verify", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    # standard button semantics
    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):
        # put focus back to the master window
        self.master.focus_set()
        self.destroy()

    def validate(self):

        try:
            hostValue= self.hostEntry.get()
            usernamveValue = self.usernameEntry.get()
            passwordValue = self.passwordEntry.get()
            
            client = Singleton(Client)
            client.loadConfig()
            client.promptForConfig()
            client.saveConfig()
            client.connect()
            client.register(hostValue, client.accountName, client.accountPass)
            time.sleep(1)
            return 1
        except Exception:
            print "Connection Failed: Unable to connect, please try again"
            return 0

    def apply(self):
        pass # override

class TreeView(Frame):

    def __init__(self, master, connectType=None):
        self.listener = Singleton(Listener)
        self.bDownFlag = False
        self.mouseFocusFlag = False
        
        self.bDownFlagServer = False
        self.mouseFocusFlagServer = False

        self.connectType = connectType
        #if self.connectType == "Server":
        self.serverConnection = Singleton(Client)

        Frame.__init__(self, master)

        vsb = ttk.Scrollbar(orient="vertical")
        hsb = ttk.Scrollbar(orient="horizontal")
        
        tree = ttk.Treeview(columns=("fullpath", "type", "size"),
            displaycolumns="size", yscrollcommand=lambda f, l: self.autoscroll(vsb, f, l),
            xscrollcommand=lambda f, l:self.autoscroll(hsb, f, l))

        vsb['command'] = tree.yview
        hsb['command'] = tree.xview
        
        tree.heading("#0", text="Directory", anchor='w')
        tree.heading("size", text="File Size", anchor='w')
        tree.column("size", stretch=300, width=300)

        self.populate_roots(tree)
        tree.bind('<<TreeviewOpen>>', self.update_tree)
        tree.bind('<Double-Button-1>', self.change_dir)
        tree.bind("<ButtonPress-1>", self.bDown)
        tree.bind("<ButtonRelease-1>", self.bUp)
        tree.bind("<Leave>", self.mouseLoseFocus)

        tree.pack(side=LEFT, fill=BOTH)
        vsb.pack(side=LEFT, fill=BOTH)
        

    def populate_tree(self, tree, node):
        if tree.set(node, "type") != 'directory':
            return

        path = tree.set(node, "fullpath")
        tree.delete(*tree.get_children(node))

        parent = tree.parent(node)
        special_dirs = [] if parent else glob.glob('.') + glob.glob('..')
        if self.connectType == None:
            for p in special_dirs + os.listdir(path):
                ptype = None
                p = os.path.join(path, p).replace('\\', '/')
                if os.path.isdir(p): ptype = "directory"
                elif os.path.isfile(p): ptype = "file"
        
                fname = os.path.split(p)[1]
                id = tree.insert(node, "end", text=fname, values=[p, ptype])
        
                if ptype == 'directory':
                    if fname not in ('.', '..'):
                        tree.insert(id, 0, text="dummy")
                        tree.item(id, text=fname)
                elif ptype == 'file':
                    size = os.stat(p).st_size
                    tree.set(id, "size", "%d bytes" % size)
        elif self.connectType == "Server":
            for p in special_dirs + self.serverConnection.getFileList():# + self.serverConnection.getListDir():
                ptype = None
                p = os.path.join(path, p).replace('\\', '/')
                if os.path.isdir(p): ptype = "directory"
                elif os.path.isfile(p): ptype = "file"
        
                fname = os.path.split(p)[1]
                id = tree.insert(node, "end", text=fname, values=[p, ptype])
        
                if ptype == 'directory':
                    if fname not in ('.', '..'):
                        tree.insert(id, 0, text="dummy")
                        tree.item(id, text=fname)
                elif ptype == 'file':
                    size = os.stat(p).st_size
                    tree.set(id, "size", "%d bytes" % size)
    
    def treePut(self):

        clientPath = self.listener.getClientPath()
        if(clientPath is None):
            return

        self.serverConnection.put(clientPath, os.path.basename(clientPath))


    def treeGet(self):
        serverPath = '/' + os.path.basename(self.listener.getServerPath())

        if os.getcwd() != "C:\\":
            clientPath = os.getcwd() + '\\' + os.path.basename(self.listener.getServerPath())
        else:
            clientPath = os.getcwd() + os.path.basename(self.listener.getServerPath())
        self.serverConnection.get(serverPath, clientPath)
        #'''

    def populate_roots(self, tree):
        if self.connectType == None:
            dir = os.path.abspath('.').replace('\\', '/')
            node = tree.insert('', 'end', text=dir, values=[dir, "directory"])
        elif self.connectType == "Server":
            dir = "/"#self.serverConnection.getCwd()
            node = tree.insert('', 'end', text=dir, values=[dir, "directory"])
        self.populate_tree(tree, node)
    
    def update_tree(self, event):
        tree = event.widget
        self.populate_tree(tree, tree.focus())
        
    def bDown(self, event):
        if self.connectType == None:
            self.listener.setbDownFlag(True)
            self.listener.setmouseFocusFlag(True)
        elif self.connectType == "Server":
            self.listener.setbDownFlagServer(True)
            self.listener.setmouseFocusFlagServer(True)
            
    def mouseLoseFocus(self, event):
        tree = event.widget
        if self.connectType == None:
            path = tree.set(tree.focus(), "fullpath")
            self.listener.setClientPath(path)
            self.listener.setmouseFocusFlagServer(True)
        elif self.connectType == "Server":
            path = tree.set(tree.focus(), "fullpath")
            self.listener.setServerPath(path)
            self.listener.setmouseFocusFlag(True)

    def bUp(self, event):
        tree = event.widget
        action = self.listener.updateEvents()
        
        if (action == 4):
            action = 0
            self.treeGet()
            self.populate_tree(tree, tree.focus())
        elif (action == 5):
            action = 0
            self.treePut()
            self.populate_tree(tree, tree.focus())

    def change_dir(self, event):
        tree = event.widget
        node = tree.focus()
        if tree.parent(node):
            if self.connectType == None:
                path = os.path.abspath(tree.set(node, "fullpath"))
                if os.path.isdir(path):
                    os.chdir(path)
                    tree.delete(tree.get_children(''))
                    self.populate_roots(tree)
            elif self.connectType == "Server":
                '''path = tree.set(node, "fullpath")
                self.serverConnection.chDir(path)
                tree.delete(tree.get_children(''))
                self.populate_roots(tree)'''
    
    def autoscroll(self, sbar, first, last):
        """Hide and show scrollbar as needed."""
        first, last = float(first), float(last)
        if first <= 0 and last >= 1:
            sbar.grid_remove()
        else:
            sbar.grid()
        sbar.set(first, last)

class Listener(object):

    _instance = None

    def __init__(self):
        self.bDownFlag = False
        self.mouseFocusFlag = False
        
        self.bDownFlagServer = False
        self.mouseFocusFlagServer = False
        
        self.clientPath = None
        self.serverPath = None
    
    def getClientPath(self):
        return self.clientPath
    
    def getServerPath(self):
        return self.serverPath

    def setClientPath(self, value):
        self.clientPath = value
        
    def setServerPath(self, value):
        self.serverPath = value

    def setbDownFlag(self, value):
        self.bDownFlag = value

    def setmouseFocusFlag(self, value):
        self.mouseFocusFlag = value
        self.mouseFocusFlagServer = not value

    def setbDownFlagServer(self, value):
        self.bDownFlagServer = value

    def setmouseFocusFlagServer(self, value):
        self.mouseFocusFlagServer = value
        self.mouseFocusFlag = not value

    def updateEvents(self):
        if ((self.bDownFlag == True and self.mouseFocusFlag == True) or (self.bDownFlagServer == True and self.mouseFocusFlagServer == True)):
            self.bDownFlag = False
            self.bDownFlagServer = False
            return 0
        
        if (self.bDownFlagServer == True and self.mouseFocusFlag == True):
            self.bDownFlag = False
            self.bDownFlagServer = False
            return 4
        
        if (self.bDownFlag == True and self.mouseFocusFlagServer == True):
            #"Client To Server"
            self.bDownFlag = False
            self.bDownFlagServer = False
            return 5
        
        self.bDownFlag = False
        self.bDownFlagServer = False
        return 0

    