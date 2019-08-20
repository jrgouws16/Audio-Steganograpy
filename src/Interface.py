# Import the needed libraries
from PyQt5 import QtWidgets, uic
from copy import deepcopy
import LSB
import wave
import fileprocessing as fp
import SignalsAndSlots
import geneticAlgorithm as GA
import ResultsAndTesting as RT

# Function for encoding using the standard LSB encoding algorithm
def LSB_encoding(bitToEncode, coverSamples, secretMessage):
        # Provide first audio channel samples and message samples to encode 
        LSB_encoding = LSB.LSB_encoding(coverSamples[0], secretMessage)
        
        # Connect the embedding progress bar
        LSB_encoding.signalEmbedding.connect(mainWindow.progressBar_embedding.setValue)
        
        # Embed the message
        LSB_encoding.encode(bitToEncode)
    
        return LSB_encoding.stegoSamples

# Function for encoding using the standard LSB encoding algorithm
def GA_encoding(coverSamples, secretMessage, key, songObj):
        originalCoverSamples = deepcopy(coverSamples[0])

        for i in range(0, len(coverSamples[0])):
            coverSamples[0][i] = "{0:016b}".format(coverSamples[0][i])

        secretMessage = "".join(map(str,secretMessage))

        # Connect the embedding progress bar
        GA.signalEmbedding.connect(mainWindow.progressBar_embedding.setValue)
    
        # Provide first audio channel samples and message samples to encode 
        stegoSamples, samplesUsed, bitsInserted = GA.insertMessage(coverSamples[0], key, "".join(map(str, secretMessage)))
             
        # Convert the binary audio samples to decimal samples
        for i in range(0, len(stegoSamples)):
            stegoSamples[i] = int(stegoSamples[i], 2)
            
        # Get the characteristics of the stego file
        infoMessage = "Embedded " + str(bitsInserted) + " bits into " + str(samplesUsed) + " samples."
        infoMessage += "\nSNR of " + str(round(RT.getSNR(originalCoverSamples[0:samplesUsed], stegoSamples[0:samplesUsed] ), 2))
        
        frameRate = songObj.getframerate() 
        
        infoMessage += ".\nCapacity of " + str(round((len(secretMessage)/(samplesUsed/frameRate))/1000, 2)) + " kbps."       
            
        # Show the results of the stego quality of the stego file
        SignalsAndSlots.showInfoMessage("Steganographic file information", infoMessage)
        
        return stegoSamples

def encode():
    stegoSamples = []
    
    # Get the cover file name from the line edit box
    coverFileName = mainWindow.lineEdit_cover.text()
    
    # Get the message file name from the line edit box
    messageFileName = mainWindow.lineEdit_message.text()
    
    # Get the stego file name to be saved to from the line edit box
    stegoFileName = mainWindow.lineEdit_stegopath.text()
    
    # Open the cover audio file
    song = wave.open(coverFileName, mode='rb')
    
    # Connect the reading cover progress bar to set how far file is read
    fp.signalExtract.connect(mainWindow.progressBar_reading.setValue)
    
            
    # Connect the write to stego progress bar
    fp.signalWriting.connect(mainWindow.progressBar_writing.setValue)
    
    # Extract the cover samples
    coverSamples = fp.extractWaveSamples(song)
    
    # Show how many samples were extracted from the cover
    mainWindow.label_cover_size.setText("Cover Samples (16 byte): " + str(len(coverSamples[0])))

    # Conncet the reading message progress bar to the embedding process
    fp.signalReadMsg.connect(mainWindow.progressBar_message.setValue)
    
    # Read the secret message file
    secretMessage = fp.getMessageBits(messageFileName)
    
    # Display the size of the secret message
    mainWindow.label_msg_size.setText("Message Size (bits): " + str(len(secretMessage)))
        
    # Get the method of encoding by seeing which radio button is checked
    # First method = Standard Least Significant Bit encoding
    if(mainWindow.radioButton_LSB.isChecked()):
        
        # User must provide LSB number to be embedded in, otherwise provide error box
        if (mainWindow.lineEdit_LSB_nr.text() == '1' or 
            mainWindow.lineEdit_LSB_nr.text() == '2' or
            mainWindow.lineEdit_LSB_nr.text() == '3' or
            mainWindow.lineEdit_LSB_nr.text() == '4'):
            
            stegoSamples = LSB_encoding(int(mainWindow.lineEdit_LSB_nr.text()), 
                                        coverSamples, 
                                        secretMessage)
            
            # Write to the stego audio file in wave format and close the song
            fp.writeStegoToFile(stegoFileName, song.getparams(), stegoSamples)
            song.close()

        # Else embed the secret message    
        else:
            SignalsAndSlots.showErrorMessage('Invalid LSB embedding position', 'Enter an integer ranging from 1 to 4')
            
    # Second method = Genetic Algorithm
    elif(mainWindow.radioButton_GA.isChecked()):
        # Get the string representation of the key in ASCII
        keyString = mainWindow.lineEdit_GA_key.text()
        
        # Convert ASCII to binary 
        binaryKey = fp.messageToBinary(keyString) 
        binaryKey = binaryKey * int((len(secretMessage) + float(len(secretMessage))/len(binaryKey)) )
        
        # If a key is too small, show error message
        if (len(binaryKey) < 40):
            SignalsAndSlots.showErrorMessage('Invalid key length', 'Enter a key of length greater than four')

        
        else:
            stegoSamples = GA_encoding(coverSamples, secretMessage, binaryKey, song)
           
            # Write to the stego audio file in wave format and close the song
            fp.writeStegoToFile(stegoFileName, song.getparams(), stegoSamples)
            song.close()

    # If no encoding algorithm is selected, throw an erro message 
    else:
        SignalsAndSlots.showErrorMessage("Invalid Encoding Algorithm selected",
                         "Select an encoding algorithm by selecting a radio button")    
                
   
def setCoverPath():
      mainWindow.lineEdit_cover.setText(fp.openFile())
      
def setMessagePath():
      mainWindow.lineEdit_message.setText(fp.openFile())
      
def setStegoPath():
      mainWindow.lineEdit_stegopath.setText(fp.saveFile())
      
def setKey():
    fileName = fp.openFile()
    fileContent = open(fileName, 'r', encoding = 'utf-8')
    mainWindow.lineEdit_GA_key.setText(fileContent.read())

if __name__ == "__main__":
    # Create a QtWidget application
    app = QtWidgets.QApplication([])

    # Load the user interface designed on Qt Designer
    mainWindow = uic.loadUi("EncodingInterface.ui")
    
    # Set the placeholder that will display the cover file path selected
    mainWindow.lineEdit_cover.setPlaceholderText("Path")
    mainWindow.lineEdit_cover.setReadOnly(True)
    
    # Set the placeholder that will display the message file path selected
    mainWindow.lineEdit_message.setPlaceholderText("Path")
    mainWindow.lineEdit_message.setReadOnly(True)
    
    # Set the placeholder that will display the steganography file path selected
    mainWindow.lineEdit_stegopath.setPlaceholderText("Path")
    mainWindow.lineEdit_stegopath.setReadOnly(True)
    
    # Set the placeholder for the key of the GA
    mainWindow.lineEdit_GA_key.setPlaceholderText("Insert Key or browse for key file (.txt)")
    
    # Hide objects at start
    mainWindow.lineEdit_GA_key.hide()
    mainWindow.pushButton_browse_key.hide()
    mainWindow.lineEdit_LSB_nr.hide()
    
    # Guide user to provide values 1, 2, 3 or 4
    mainWindow.lineEdit_LSB_nr.setPlaceholderText("LSB 1-4")
    
    # Connect the browse key to the setKey function
    mainWindow.pushButton_browse_key.clicked.connect(setKey)
    
    # Connect the encode pushbutton to the encode function when clicked
    mainWindow.pushButton_encode.clicked.connect(encode)
    
    # Connect the browse cover, message and stego file to slots
    mainWindow.pushButton_browse_cover.clicked.connect(setCoverPath)
    mainWindow.pushButton_browse_message.clicked.connect(setMessagePath)
    mainWindow.pushButton_browse_stego.clicked.connect(setStegoPath)
    
    # Set the progress on the progress bars to 0 to start with
    mainWindow.progressBar_reading.setValue(0)
    mainWindow.progressBar_embedding.setValue(0)
    mainWindow.progressBar_writing.setValue(0)
    mainWindow.progressBar_message.setValue(0)
    
    # Set the GUI background to specified image
    mainWindow.setStyleSheet("QMainWindow {border-image: url(Media/music.jpg) 0 0 0 0 stretch stretch}")
    
    # Execute and show the user interface
    mainWindow.show()
    app.exec()
