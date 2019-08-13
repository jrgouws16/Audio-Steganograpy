from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import *

# Function to display custom error message
def showErrorMessage(title, message):
    QMessageBox.critical(None, title, message)
    
# Function to display custom error message
def showInfoMessage(title, message):
    QMessageBox.information(None, title, message)

class SigSlot(QObject):
    # Define a new signal called 'trigger' that has no arguments.
    trigger = pyqtSignal(float)

    # Connect to a slot
    def connect(self, function):
        self.trigger.connect(function)

# Exaple Usage
# app = QtWidgets.QApplication([])
# mySignal = SigSlot()
# mainWindow = uic.loadUi("test.ui")
# mySignal.connect(mainWindow.progressBar.setValue)
# mySignal.trigger.emit(5)
# mainWindow.show()
# app.exec()