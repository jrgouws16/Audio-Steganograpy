from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox


class files(QObject):
    my_signal = pyqtSignal()
    
    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)
    
    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)

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