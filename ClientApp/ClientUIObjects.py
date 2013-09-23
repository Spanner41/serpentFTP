'''
Client UI Objects

@author: Joseph Kostreva, Brady Steed
'''
from Tkinter import *
from ClientObjects import Connection
import os

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

    #
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
            
            server = Connection(hostname=hostValue,username=usernamveValue,password=passwordValue)
            server.connect()
            self.result = server
            return 1
        except Exception:
            print "Connection Failed: Unable to connect, please try again"
            return 0

    def apply(self):

        pass # override