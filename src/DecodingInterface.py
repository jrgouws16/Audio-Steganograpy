# Import the needed libraries
from PyQt5 import QtWidgets, uic
import LSB
import wave
import fileprocessing as fp
import SignalsAndSlots

def LSB_decoding(stegoFileName):
    try:
        song = wave.open(stegoFileName, mode='rb')

        # Create a object for retrieving samples of audio cover file
        fp.signalExtract.connect(mainWindow.progressBar_reading.setValue)
        stegoSamples = fp.extractWaveSamples(song)
        

        LSB_decoding = LSB.LSB_decoding(stegoSamples[0])
        LSB_decoding.signalExtractingMessage.connect(mainWindow.progressBar_extracting.setValue)
        secret_message = LSB_decoding.decode(int(mainWindow.lineEdit_bits_to_extract.text()), int(mainWindow.lineEdit_LSB_nr.text()))

        fp.signalWriteMsg.connect(mainWindow.progressBar_writing.setValue)
        fp.writeMessageBitsToFile(secret_message, mainWindow.lineEdit_msgname.text())

        song.close()

    except:
        SignalsAndSlots.showErrorMessage("Invalid stego filename provided", "The steganographic file name provided does not exist or inserted wrongly")

def decode():
    stegoFileName = mainWindow.lineEdit_stego.text()

    if (stegoFileName == ""):
        SignalsAndSlots.showErrorMessage("Invalid Stego File Name",
                         "Check name and make sure that it has a .wav extention")

    elif(mainWindow.radioButton_LSB.isChecked()):
        if (mainWindow.lineEdit_LSB_nr.text() == ''):
            SignalsAndSlots.showErrorMessage('Invalid LSB embedding position', 'Enter an integer ranging from 1 to 4')
        else:
            LSB_decoding(stegoFileName)

    elif(mainWindow.radioButton_GA.isChecked()):
        print('Genetic Algorithm is executing')

    else:
        SignalsAndSlots.showErrorMessage("Invalid Encoding Algorithm selected",
                         "Select an encoding algorithm by selecting a radio button")

def setMessagePath():
      mainWindow.lineEdit_msgname.setText(fp.saveMessage())
      
def setStegoPath():
      mainWindow.lineEdit_stego.setText(fp.openFile())

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    mainWindow = uic.loadUi("DecodingInterface.ui")
    mainWindow.lineEdit_stego.setPlaceholderText("Path")
    mainWindow.lineEdit_stego.setReadOnly(True)
    mainWindow.lineEdit_msgname.setPlaceholderText("Path")
    mainWindow.lineEdit_msgname.setReadOnly(True)
    mainWindow.lineEdit_LSB_nr.setPlaceholderText("LSB 1-4")
    mainWindow.progressBar_reading.setValue(0)
    mainWindow.progressBar_extracting.setValue(0)
    mainWindow.progressBar_writing.setValue(0)
    mainWindow.setStyleSheet("QMainWindow {border-image: url(C:/Users/project/Desktop/EPR practical/Media/music.jpg) 0 0 0 0 stretch stretch}")
    mainWindow.pushButton_decode.clicked.connect(decode)
    mainWindow.pushButton_browse_stego.clicked.connect(setStegoPath)
    mainWindow.pushButton_browse_message.clicked.connect(setMessagePath)
    mainWindow.show()
    app.exec()
