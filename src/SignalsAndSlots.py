from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
import tkinter as tk
from tkinter import filedialog

########################################################################################################################
#####################                          General usefull functions                    ############################
########################################################################################################################
def openFile():
    # Create a tkinter main window
    root = tk.Tk()

    # Hide the main window                           
    root.withdraw()  

    # Allow user to select the file path through file browsing                            
    return filedialog.askopenfilename()          

def saveFile():
    root = tk.Tk()
    root.withdraw()
    return filedialog.asksaveasfilename(initialdir = "/",
                                        title = "Select file",
                                        filetypes = (("(.wav) files","*.wav"),
                                                     ("all files","*.*")))

def saveMessage():
    root = tk.Tk()
    root.withdraw()
    return filedialog.asksaveasfilename(initialdir = "/",
                                        title = "Select file",
                                        filetypes = (("(.txt) files","*.txt"), 
                                                     (".pdf) files","*.pdf"),
                                                     ("all files","*.*")))







class SigSlot(QObject):
    # Define a new signal called 'trigger' that has no arguments.
    trigger = pyqtSignal(float)

    # Connect to a slot
    def connect(self, function):
        self.trigger.connect(function)

# Function to display custom error message
def showErrorMessage(title, message):
    QMessageBox.critical(None, title, message)
    
# Function to display custom error message
def showInfoMessage(title, message):
    QMessageBox.information(None, title, message)

class fileSaveSigSlot(QObject):

    # Define a new signal called 'trigger' that has no arguments.
    trigger = pyqtSignal()
    filePath = ""
    setPath = False

    def connect(self):
        # Connect the trigger signal to a slot.
        self.trigger.connect(self.handle_trigger)

    def emit(self):
        # Emit the signal.
        self.trigger.emit()

    def handle_trigger(self):
          self.filePath = saveFile()
          self.setPath = True
          
class showInfoSigSlot(QObject):

    # Define a new signal called 'trigger' that has no arguments.
    trigger = pyqtSignal()
    info = ""
    title = ""

    def connect(self):
        # Connect the trigger signal to a slot.
        self.trigger.connect(self.handle_trigger)

    def emit(self):
        # Emit the signal.
        self.trigger.emit()

    def handle_trigger(self):
          showInfoMessage(self.title, self.info)

# Exaple Usage
# app = QtWidgets.QApplication([])
# mySignal = SigSlot()
# mainWindow = uic.loadUi("test.ui")
# mySignal.connect(mainWindow.progressBar.setValue)
# mySignal.trigger.emit(5)
# mainWindow.show()
# app.exec()