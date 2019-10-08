import tkinter as tk
from tkinter import filedialog
import numpy as np
import sys
import struct
import SignalsAndSlots
import wave
import scipy.io.wavfile as scWave

#from scipy.io import wavfile
#import numpy as np

signalWriting = SignalsAndSlots.SigSlot()

# Create a signal to emit the progress of extracting samples
signalExtract = SignalsAndSlots.SigSlot()

# Create a signal to emit the progress of extracting samples
signalReadMsg = SignalsAndSlots.SigSlot()

# Create a signal to emit the progress of writing to mesage file
signalWriteMsg = SignalsAndSlots.SigSlot()

###############################################################################
#                          General usefull functions                    #######
###############################################################################
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

###############################################################################
#               Functions for reading and writing to message file       #######
###############################################################################

# Takes a text file and returns a integer list of the bits to be embedded
def getMessageBits(file_path):
    # Open the file to be read and get the length
    file = open(file_path, 'rb')                   
    messageLength = len(file.read())
    progress = 0
    
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
        if ((totalBytes+1)*100/messageLength > progress):
            progress = (totalBytes+1)*100/messageLength
            signalReadMsg.trigger.emit(progress)

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
    
    # Write eight bits at a time and delete the eight bits
    while (len(totalMessageBits) > 0):
        # Convert eight bit sample to integer value and convert to a byte format
        file.write((int(totalMessageBits[0:8], 2).to_bytes(1, byteorder = sys.byteorder)))
        
        # Delete the byte that was written
        totalMessageBits = totalMessageBits[8:]
                

    file.close()

def binaryStringToASCII(binaryString):
    
    ASCII = ""
    
    while (len(binaryString) % 8 != 0):
        binaryString = list(binaryString)
        binaryString = binaryString[1:]
        binaryString = "".join(binaryString)
        
    while (len(binaryString) > 0):
        ASCII += chr(int(binaryString[0:8], 2))
        binaryString = binaryString[8:]
        
    return ASCII    

#               For reading, writing and extracting samples for wave files    #
###############################################################################

# Function to return the samples of a wave audio file.
# Returns two integer lists of samples for two channels
# The second list will be empty if the wave file is mono
# NB! This will only be used for the cover filie samples
#def extractWaveSamples(waveObject):
#    samplesChannelOne = []
#    samplesChannelTwo = []
#    
#    # Get the wave file parameters
#    nchannels, sampwidth, framerate, nframes, comptype, compname = waveObject.getparams()
#
#    # Read two bytes for mono (<1h) in little endian format
#    # Read four bytes for stereo (<2h) in little endian format
#    format = '<{}h'.format(nchannels)
#
#    for index in range(nframes):
#        # Read one frame
#        frame = waveObject.readframes(1)
#
#        # Unpack the frame to integer value            
#        data = struct.unpack(format, frame) 
#        
#        # First channel value added to channel one
#        samplesChannelOne.append(data[0])         
#
#        # Prevents overflow when inserting the message
#        if (samplesChannelOne[-1] <= -32768):       
#            samplesChannelOne[-1] += 1
#
#        # Do the second channel
#        if (nchannels == 2):
#            samplesChannelTwo.append(data[1])
#
#            if (samplesChannelTwo[-1] <= -32768):
#                samplesChannelTwo[-1] += 1
#       
#    return samplesChannelOne, samplesChannelTwo

def getWaveSamples(path):
      
      while (1):
          try:
              rate, samples = scWave.read(path)
              break
          except Exception:
              print("Exception in reading the wave file, retrying")
      
      samplesOne = []
      samplesTwo = []
            
      for i in range(0, len(samples)):
            if (len(samples.shape) == 2):
                  samplesOne.append(samples[i][0])
                  samplesTwo.append(samples[i][1])
            else:
                  samplesOne.append(samples[i])
                  
      return samplesOne, samplesTwo, rate

def extractWaveMessage(path):
    samplesChannelOne, samplesChannelTwo, framerate = getWaveSamples(path)
    
    for index in range(0, len(samplesChannelOne)):
        
        # Convert to binary
        samplesChannelOne[index] = np.binary_repr(samplesChannelOne[index], 16)
        
    return samplesChannelOne, samplesChannelTwo

# Inverse of numpy binary_representation, but only for 16 bit samples
def binaryToInt(binaryString):
       
    if (binaryString[0] == '1'):
        return int(binaryString, 2)-(1<<16)
    else:
        return int(binaryString, 2)


def writeWaveMessageToFile(binString, file):
      samples = []
      rate = 8192
            
      while (len(binString) % 16 != 0):
            binString = binString[:-1]
   
      while (len(binString) > 0):
            binSample = binString[0:16]
            decSample = binaryToInt(binSample)
            samples.append(decSample)
            binString = binString[16:]
      
      samples = np.asarray(samples,dtype=np.int16,order='C')
      scWave.write(file, rate, samples)
      
# Prints the wave file parameters in the terminal
def returnParameters(self):
    print("Channels:", self.nchannels)
    print("Sample width (bytes per sample):", self.sampwidth)
    print("Framerate (sampling rate):", self.framerate)
    print("Number of samples:", self.nframes)

###############################################################################
#              For writing steganography samples to a wav file after encoding #
###############################################################################

# Write the stego samples to the stego file        
def writeStegoToFile(fileName, parameters, samples):
    byteSamples = []
    with wave.open(fileName, 'wb') as fd:
        fd.setparams(parameters)
        fd.setnchannels(1)
    
        for i in range(len(samples)):
            byteSamples.append(struct.pack('<h', samples[i]))
                      
        fd.writeframes(b''.join(byteSamples))

            
    fd.close()

###############################################################################
###############################################################################
###############################################################################
    


    