# Import the needed libraries
from PyQt5 import QtWidgets, uic
import LSB
import wave
import fileprocessing as fp
import SignalsAndSlots

def LSB_encoding(coverFileName, messageFileName, bitToEncode, stegoFileName):
    try:
        song = wave.open(coverFileName, mode='rb')
        
        fp.signalExtract.connect(mainWindow.progressBar_reading.setValue)
        cover_samples = fp.extractWaveSamples(song)
        mainWindow.label_cover_size.setText("Cover Samples (16 byte): " + str(len(cover_samples[0])))

        fp.signalReadMsg.connect(mainWindow.progressBar_message.setValue)
        secret_message = fp.getMessageBits(messageFileName)
        mainWindow.label_msg_size.setText("Message Size (bits): " + str(len(secret_message)))

        if (len(cover_samples[0]) < len(secret_message)):
            SignalsAndSlots.showErrorMessage("Cover file too small",
                                             "The cover file is too small to embed the secret message. "
                                             "Either provide a larger cover file or a smaller message")
        else:
            LSB_encoding = LSB.LSB_encoding(cover_samples[0], secret_message)
            LSB_encoding.signalWriting.connect(mainWindow.progressBar_writing.setValue)
            LSB_encoding.signalEmbedding.connect(mainWindow.progressBar_embedding.setValue)
            LSB_encoding.encode(bitToEncode)
            LSB_encoding.writeStegoToFile(stegoFileName, song.getparams())

        song.close()

    except:
        SignalsAndSlots.showErrorMessage('Cover file does not exist', 'The filename specified for the cover file does not exist')


def encode():
    coverFileName = mainWindow.lineEdit_cover.text()
    messageFileName = mainWindow.lineEdit_message.text()
    stegoFileName = mainWindow.lineEdit_stegopath.text()

    if(mainWindow.radioButton_LSB.isChecked()):
        if (mainWindow.lineEdit_LSB_nr.text() == ''):
            SignalsAndSlots.showErrorMessage('Invalid LSB embedding position', 'Enter an integer ranging from 1 to 4')
        else:
            LSB_encoding(coverFileName, messageFileName, int(mainWindow.lineEdit_LSB_nr.text()), stegoFileName)

    elif(mainWindow.radioButton_GA.isChecked()):
        print('Genetic Algorithm is executing')

    else:
        SignalsAndSlots.showErrorMessage("Invalid Encoding Algorithm selected",
                         "Select an encoding algorithm by selecting a radio button")
        
def setCoverPath():
      mainWindow.lineEdit_cover.setText(fp.openFile())
      
def setMessagePath():
      mainWindow.lineEdit_message.setText(fp.openFile())
      
def setStegoPath():
      mainWindow.lineEdit_stegopath.setText(fp.saveFile() + '.wav')

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    mainWindow = uic.loadUi("EncodingInterface.ui")
    mainWindow.lineEdit_cover.setPlaceholderText("Path")
    mainWindow.lineEdit_cover.setReadOnly(True)
    mainWindow.lineEdit_message.setPlaceholderText("Path")
    mainWindow.lineEdit_message.setReadOnly(True)
    mainWindow.lineEdit_stegopath.setPlaceholderText("Path")
    mainWindow.lineEdit_stegopath.setReadOnly(True)
    mainWindow.lineEdit_LSB_nr.setPlaceholderText("LSB 1-4")
    mainWindow.pushButton_encode.clicked.connect(encode)
    mainWindow.pushButton_browse_cover.clicked.connect(setCoverPath)
    mainWindow.pushButton_browse_message.clicked.connect(setMessagePath)
    mainWindow.pushButton_browse_stego.clicked.connect(setStegoPath)
    mainWindow.progressBar_reading.setValue(0)
    mainWindow.progressBar_embedding.setValue(0)
    mainWindow.progressBar_writing.setValue(0)
    mainWindow.progressBar_message.setValue(0)
    mainWindow.setStyleSheet("QMainWindow {border-image: url(C:/Users/project/Desktop/EPR practical/Media/music.jpg) 0 0 0 0 stretch stretch}")
    mainWindow.show()
    app.exec()
