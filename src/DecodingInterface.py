# Import the needed libraries
from PyQt5 import QtWidgets, uic
import LSB
import wave
import fileprocessing as fp
import SignalsAndSlots
import geneticAlgorithm as GA

# Function to extract the message from the stego file making use of 
# Standard Least Significant Bit Encoding
def LSB_decoding(stegoSamples):
    
    # Create a LSB object for decoding
    LSB_decoding = LSB.LSB_decoding(stegoSamples[0])
    
    # Extract the message bits
    LSB_decoding.signalExtractingMessage.connect(mainWindow.progressBar_extracting.setValue)
    
    # Retrieve the message
    secretMessage = LSB_decoding.decode(int(mainWindow.lineEdit_bits_to_extract.text()), int(mainWindow.lineEdit_LSB_nr.text()))

    return secretMessage
        
# Function to extract the message from the stego file making use of 
# Genetic Algorithm
def GA_decoding(stegoSamples, key):
   
    # Convert integer samples to binary samples
    for i in range(0, len(stegoSamples[0])):
        stegoSamples[0][i] = "{0:016b}".format(stegoSamples[0][i])
        
    # Connect the extracting algorithm progress to the progress bar
    GA.signalExtractingMessage.connect(mainWindow.progressBar_extracting.setValue)
    
    # Extract secret message
    secretMessage = GA.extractMessage(stegoSamples[0], key)
        
    return secretMessage
        
# Function for extracting the message using different stegangography algorithms
def decode():
    
    # Get the filename of the stego audio file
    stegoFileName = mainWindow.lineEdit_stego.text()

    #try:
    # Open the steganography file
    song = wave.open(stegoFileName, mode='rb')

    # Connect the reading stego file to the progress bar
    fp.signalExtract.connect(mainWindow.progressBar_reading.setValue)
    
    # Extract the samples from the stego file
    stegoSamples = fp.extractWaveSamples(song)

    # Standard Least Significant Bit Decoding
    if (mainWindow.radioButton_LSB.isChecked()):
        # User must provide LSB number to extract, otherwise provide error box
        if (mainWindow.lineEdit_LSB_nr.text() == '1' or 
            mainWindow.lineEdit_LSB_nr.text() == '2' or
            mainWindow.lineEdit_LSB_nr.text() == '3' or
            mainWindow.lineEdit_LSB_nr.text() == '4'):
            
            secretMessage = LSB_decoding(stegoSamples)
            
            # Connect the writing message to file to the progress bar
            fp.signalWriteMsg.connect(mainWindow.progressBar_writing.setValue)
            
            # Write the message bits to a file and close the steganography file
            fp.writeMessageBitsToFile(secretMessage, mainWindow.lineEdit_msgname.text())
            song.close()
            
        else:
            SignalsAndSlots.showErrorMessage('Invalid LSB embedding position', 
                                             'Enter an integer ranging from 1 to 4')
        
    # Genetic Algorithm decoding
    elif(mainWindow.radioButton_GA.isChecked()):
        keyString = mainWindow.lineEdit_GA_key.text()
        binaryKey = fp.messageToBinary(keyString)
        secretMessage = GA_decoding(stegoSamples, binaryKey)
        
        # Connect the writing message to file to the progress bar
        fp.signalWriteMsg.connect(mainWindow.progressBar_writing.setValue)
        
        # Write the message bits to a file and close the steganography file
        fp.writeMessageBitsToFile(secretMessage, mainWindow.lineEdit_msgname.text())
        song.close()
        
        
    # No radio button selected
    else:
        SignalsAndSlots.showErrorMessage("Invalid Encoding Algorithm selected",
                         "Select an encoding algorithm by selecting a radio button")
            
    # Throw an exception if the file does not exist
    #except:
     #   SignalsAndSlots.showErrorMessage("Invalid stego filename provided", 
      #                                   "The steganographic file name provided does not exist or inserted wrongly")


# Slot to set the file path to save the secret message in
def setMessagePath():
      mainWindow.lineEdit_msgname.setText(fp.saveMessage())
      
# Slot to set the file path to get the stego file      
def setStegoPath():
      mainWindow.lineEdit_stego.setText(fp.openFile())
      
def setKey():
    fileName = fp.openFile()
    fileContent = open(fileName, 'r', encoding = 'utf-8')
    mainWindow.lineEdit_GA_key.setText(fileContent.read())

if __name__ == "__main__":
    
    # Create a QtWidget application
    app = QtWidgets.QApplication([])

    # Load the user interface designed on Qt Designer
    mainWindow = uic.loadUi("DecodingInterface.ui")
    
    # Set the placeholder that will display the stego file path selected
    mainWindow.lineEdit_stego.setPlaceholderText("Path")
    mainWindow.lineEdit_stego.setReadOnly(True)
    
    # Set the placeholder that will display the message file path selected
    mainWindow.lineEdit_msgname.setPlaceholderText("Path")
    mainWindow.lineEdit_msgname.setReadOnly(True)
    
    # Guide user to provide values 1, 2, 3 or 4
    mainWindow.lineEdit_LSB_nr.setPlaceholderText("LSB 1-4")
    
    # Set the progress bar progress to 0
    mainWindow.progressBar_reading.setValue(0)
    mainWindow.progressBar_extracting.setValue(0)
    mainWindow.progressBar_writing.setValue(0)
    
    # Objects to hide at the start of the GUI
    mainWindow.lineEdit_bits_to_extract.hide()
    mainWindow.label_bits_to_extract.hide()
    mainWindow.lineEdit_LSB_nr.hide()
    mainWindow.lineEdit_GA_key.hide()
    
    # Connect the signals and slots
    mainWindow.pushButton_decode.clicked.connect(decode)
    mainWindow.pushButton_browse_stego.clicked.connect(setStegoPath)
    mainWindow.pushButton_browse_message.clicked.connect(setMessagePath)
    mainWindow.pushButton_browse_key.clicked.connect(setKey)
    
    # Set the GUI background to specified image
    mainWindow.setStyleSheet("QMainWindow {border-image: url(Media/music.jpg) 0 0 0 0 stretch stretch}")
    mainWindow.show()
    app.exec()
