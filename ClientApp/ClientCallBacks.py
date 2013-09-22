'''
Client UI CallBack functions

@author: Joseph Kostreva, Brady Steed
'''

from Tkinter import *
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfile
import tkMessageBox
import sys

class CallBacks():

    @staticmethod
    def connectCallBack():
        print "called the connect callback!"

    @staticmethod
    def openCallBack():
        
        # Path to remote host
        pathToRemoteHost = "~/Desktop/"

        fileName = askopenfilename(initialdir=pathToRemoteHost,
                                   filetypes=(("Image files", "*.jpg;*.png;*.bmp"),
                                           ("Video files", "*.mpg;*.avi;*.wmv"),
                                           ("Audio files", "*.mp3;*.wav"),
                                           ("All files", "*.*") ))
        if fileName:
            try:
                print("""here it comes: self.settings["template"].set(fname)""")
            except:
                tkMessageBox.showerror("Open Source File", "Failed to read file\n'%s'" % fileName)
            return


    @staticmethod
    def saveCallBack():
        
        # Path to client
        pathToClient = "C:/"
        initialFileName = "myfile.txt"

        fileName = asksaveasfile(mode='w',
                                 initialfile=initialFileName,
                                 initialdir=pathToClient,
                                 filetypes=(("Image files", "*.jpg;*.png;*.bmp"),
                                           ("Video files", "*.mpg;*.avi;*.wmv"),
                                           ("Audio files", "*.mp3;*.wav"),
                                           ("All files", "*.*") ))

        if fileName:
            try:
                # Write data to file here
                fileName.write("Writing info...")
            except:
                tkMessageBox.showerror("Open Source File", "Failed to read file\n'%s'" % fileName)
            return


    @staticmethod
    def exitCallBack():
        # Perform cleanup and necessary functionality before closing
        # TODO if needed...
        
        # Close the program
        sys.exit(0)

    @staticmethod
    def aboutCallBack():
        tkMessageBox.showinfo(title="About", message=u'Program developed by: \nJoseph Kostreva and Brady Steed')
