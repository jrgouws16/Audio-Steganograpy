import tkinter as tk
from tkinter import filedialog
import sys
import struct
import SignalsAndSlots
import wave

signalWriting = SignalsAndSlots.SigSlot()

# Create a signal to emit the progress of extracting samples
signalExtract = SignalsAndSlots.SigSlot()

# Create a signal to emit the progress of extracting samples
signalReadMsg = SignalsAndSlots.SigSlot()

# Create a signal to emit the progress of writing to mesage file
signalWriteMsg = SignalsAndSlots.SigSlot()

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

########################################################################################################################
#####################               Functions for reading and writing to message file       ############################
########################################################################################################################

# Takes any message file and returns a integer list of the bits
def getMessageBits(file_path):
    # Open the file to be read and get the length
    file = open(file_path, 'rb')                   
    messageLength = len(file.read())
    
    # Reopen file to read from beginning
    file = open(file_path, 'rb') 

    # Samples to be returned                  
    totalSamples = '' 
    
    totalBytes = 0

    while (1):
        # Read one byte of the file
        byte = file.read(1)                        
        totalBytes += 1
        
        # Transmit signal to display progress on GUI
        signalReadMsg.trigger.emit((totalBytes+1)*100/messageLength)

        # Break if the end of the file is reached
        if (len(byte) == 0):                       
            break

        # Format in 8-bit string samples
        sample = "{0:08b}".format(int.from_bytes(byte, byteorder=sys.byteorder))
        
        totalSamples += sample                                                     

    file.close()

    # Return integer list of samples
    return list(map(int, totalSamples))                                             


# Convert an eight bit string to list of eight integers
def messageToBinary(message):
    return ''.join('{0:08b}'.format(ord(x), 'b') for x in message)

# Write the binary message to a file
def writeMessageBitsToFile(totalMessageBits, file_path):
    file = open(file_path, 'wb')                       

    # Number of messsage bits to keep track of progress on GUI
    originalSize = len(totalMessageBits)

    # Write eight bits at a time and delete the eight bits
    while (len(totalMessageBits) > 0):
        # Convert eight bit sample to integer value and convert to a byte format
        file.write((int(totalMessageBits[0:8], 2).to_bytes(1, byteorder = sys.byteorder)))
        
        # Delete the byte that was written
        totalMessageBits = totalMessageBits[8:]
        
        # Send signal to update GUI
        signalWriteMsg.trigger.emit(100-100.0*len(totalMessageBits)/originalSize)

    file.close()

########################################################################################################################
#####################               For reading, writing and extracting samples for wave files    ######################
########################################################################################################################

# Function to return the samples of a wave audio file.
# Returns two integer lists of samples for two channels
# The second list will be empty if the wave file is mono

def extractWaveSamples(waveObject):
    samplesChannelOne = []
    samplesChannelTwo = []
    
    # Get the wave file parameters
    nchannels, sampwidth, framerate, nframes, comptype, compname = waveObject.getparams()

    # Read two bytes for mono (<1h) in little endian format
    # Read four bytes for stereo (<2h) in little endian format
    format = '<{}h'.format(nchannels)

    for index in range(nframes):
        # Read one frame
        frame = waveObject.readframes(1)

        # Unpack the frame to integer value            
        data = struct.unpack(format, frame) 
        
        # First channel value added to channel one
        samplesChannelOne.append(data[0])         

        # Prevents overflow when inserting the message
        if (samplesChannelOne[-1] == -32768):       
            samplesChannelOne[-1] += 1

        # Do the second channel
        if (nchannels == 2):
            samplesChannelTwo.append(data[1])

            if (samplesChannelTwo[-1] == -32768):
                samplesChannelTwo[-1] += 1

        signalExtract.trigger.emit((index+1) * 100 / nframes)

    return samplesChannelOne, samplesChannelTwo

# Prints the wave file parameters in the terminal
def returnParameters(self):
    print("Channels:", self.nchannels)
    print("Sample width (bytes per sample):", self.sampwidth)
    print("Framerate (sampling rate):", self.framerate)
    print("Number of samples:", self.nframes)


########################################################################################################################
#####################              For writing steganography samples to a wav file after encoding ######################
########################################################################################################################

# Write the stego samples to the stego file        
def writeStegoToFile(fileName, parameters, samples):
    with wave.open(fileName, 'wb') as fd:
        fd.setparams(parameters)
    
        for i in range(len(samples)):
            fd.writeframes(struct.pack('<h', samples[i]))
            signalWriting.trigger.emit((i+1)*100/(len(samples)))
        
    fd.close()

########################################################################################################################
########################################################################################################################
########################################################################################################################