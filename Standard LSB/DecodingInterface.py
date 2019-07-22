# Import the needed libraries
from PyQt5 import QtWidgets, uic
import LSB
import audioOperations
import wave
import fileprocessing
import SignalsAndSlots

def LSB_decoding(stegoFileName):
    try:
        song = wave.open('C:/Users/project/Desktop/EPR practical/Media_encoded/' + stegoFileName, mode='rb')

        # Create a object for retrieving samples of audio cover file
        stego = audioOperations.stegoTools(song, "Stego")
        stego.extractingSamples.connect(mainWindow.progressBar_reading.setValue)
        stego.extractSamples()

        LSB_decoding = LSB.LSB_decoding(stego.returnSamplesChannelOne())
        LSB_decoding.signalExtractingMessage.connect(mainWindow.progressBar_extracting.setValue)
        secret_message = LSB_decoding.decode(int(mainWindow.lineEdit_bits_to_extract.text()), int(mainWindow.lineEdit_LSB_nr.text()))


        messageProcessing = fileprocessing.MessageFileDecoding(mainWindow.lineEdit_msgname.text())
        messageProcessing.signalWriteMessage.connect(mainWindow.progressBar_writing.setValue)
        messageProcessing.writeTotalSamplesToFile(secret_message)

        song.close()

    except:
        SignalsAndSlots.showErrorMessage("Invalid stego filename provided", "The steganographic file name provided does not exist or inserted wrongly")

def decode():
    stegoFileName = mainWindow.lineEdit_stego.text()

    if (stegoFileName == ""):
        SignalsAndSlots.showErrorMessage("Invalid Stego File Name",
                         "Check name and make sure that it has a .wav extention")

    elif(mainWindow.radioButton_LSB.isChecked()):
        print("Least Significant bit steganography decoding is executing")
        if (mainWindow.lineEdit_LSB_nr.text() == ''):
            SignalsAndSlots.showErrorMessage('Invalid LSB embedding position', 'Enter an integer ranging from 1 to 4')
        else:
            LSB_decoding(stegoFileName)

    elif(mainWindow.radioButton_GA.isChecked()):
        print('Genetic Algorithm is executing')

    else:
        SignalsAndSlots.showErrorMessage("Invalid Encoding Algorithm selected",
                         "Select an encoding algorithm by selecting a radio button")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    mainWindow = uic.loadUi("DecodingInterface.ui")
    mainWindow.lineEdit_stego.setPlaceholderText("filename")
    mainWindow.lineEdit_LSB_nr.setPlaceholderText("LSB 1-4")
    mainWindow.progressBar_reading.setValue(0)
    mainWindow.progressBar_extracting.setValue(0)
    mainWindow.progressBar_writing.setValue(0)
    mainWindow.setStyleSheet("QMainWindow {border-image: url(C:/Users/project/Desktop/EPR practical/Media/music.jpg) 0 0 0 0 stretch stretch}")
    mainWindow.pushButton_decode.clicked.connect(decode)
    mainWindow.show()
    app.exec()
