'''
Main client UI functionality

@author: Joseph Kostreva, Brady Steed
'''
from Tkinter import *
import ttk
from ClientCallBacks import CallBacks
from ClientUIObjects import StatusBar

class UI(object):

    '''
    Constructor
    '''
    def __init__(self):
        pass

    def runClientUI(self):
        root = Tk()

        # Set window minimum size
        root.minsize(UIConstants.MINIMUM_SIZE_LENGTH, UIConstants.MINIMUM_SIZE_WIDTH)

        # Give title to application
        root.wm_title(UIConstants.STORAGE_SERVICE_TITLE)

        # Give an icon to the application
        root.wm_iconbitmap('folder.ico')

        self.createDefaultMenu(root)

        # Create status bar and set current status
        status = StatusBar(root)
        status.pack(side=BOTTOM, fill=X)
        status.set("Currently working in beta mode")

        # Create a progress bar for downloads
        downloadBar = ttk.Progressbar(
            root, orient="horizontal",
            length=UIConstants.DOWNLOAD_BAR_LENGTH, mode="determinate",
            )
        downloadBar.pack(side=BOTTOM)

        # Note to update progress bar call
        # downloadBar.step({RANGE1-100})

        # Create top window contents
        root.mainloop()

    def createDefaultMenu(self, root):
        menu = Menu(root)
        root.config(menu=menu)

        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Connect...", command=CallBacks.connectCallBack)
        filemenu.add_command(label="Open...", command=CallBacks.openCallBack)
        filemenu.add_command(label="Save...", command=CallBacks.saveCallBack)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=CallBacks.exitCallBack)

        helpmenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About...", command=CallBacks.aboutCallBack)

class UIConstants():

    # Minimum window size length
    MINIMUM_SIZE_LENGTH = 300

    # Minimum window size width
    MINIMUM_SIZE_WIDTH = 300

    # Storage Service Name
    STORAGE_SERVICE_TITLE = "Cool Storage Service"

    # Download bar length
    DOWNLOAD_BAR_LENGTH = 300
