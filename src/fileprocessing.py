import tkinter as tk
from tkinter import filedialog
import sys
import struct

########################################################################################################################
#####################                          General usefull functions                    ############################
########################################################################################################################
def browseFilename():
    root = tk.Tk()  # Create a tkinter main window
    root.withdraw()  # Hide the main window
    return filedialog.askopenfilename()  # Allow user to select the file path through file browsing

########################################################################################################################
#####################               Functions for reading and writing to message file       ############################
########################################################################################################################

# Takes any message file and returns a integer list of the bits
def getMessageBits():
    root = tk.Tk()                                 # Create a tkinter main window
    root.withdraw()                                # Hide the main window
    file_path = filedialog.askopenfilename()       # Allow user to select the file path through file browsing
    file = open(file_path, 'rb')                   # Open the file to be read

    totalSamples = ''                              # Samples to be returned
    while (1):
        byte = file.read(1)                        # Read one byte of the file

        if (len(byte) == 0):                       # Break if the end of the file is reached
            break

        sample = "{0:08b}".format(int.from_bytes(byte, byteorder=sys.byteorder))    # Format in 8-bit samples
        totalSamples += sample                                                      # Add to total samples

    file.close()

    return list(map(int, totalSamples))                                             # Return integer samples


# Convert an eight bit string to list of eight integers
def messageToBinary(message):
    return list(map(int, ''.join('{0:08b}'.format(ord(x), 'b') for x in message)))

# Write the binary message to a file
def writeMessageBitsToFile(totalMessageBits):
    file_path = browseFilename()
    file = open(file_path, 'wb')                        # Open the file to be written

    # Write eight bits at a time and delete the eight bits
    while (len(totalMessageBits) > 0):
        file.write((int(samples[0:8], 2).to_bytes(1, byteorder = sys.byteorder)))
        samples = samples[8:]

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
    nchannels, sampwidth, framerate, nframes, comptype, compname = waveObject.getparams()

    # Read two bytes for mono (<1h) in little endian format
    # Read four bytes for stereo (<2h) in little endian format
    format = '<{}h'.format(nchannels)

    for index in range(nframes):
        frame = self.audio.readframes(1)            # Read frame
        data = struct.unpack(format, frame)         # Unpack frame from sixteen bit sample to an integer
        samplesChannelOne.append(data[0])           # First (left) channel only

        if (samplesChannelOne[-1] == -32768):       # Prevents overflow when inserting the message
            samplesChannelOne[-1] += 1

        if (nchannels == 2):
            samplesChannelTwo.append(data[1])

            if (samplesChannelTwo[-1] == -32768):
                samplesChannelTwo[-1] += 1

        return samplesChannelOne, samplesChannelTwo

# Prints the wave file parameters in the terminal
def returnParameters(self):
    # Get input file parameters
    print("Channels:", self.nchannels)
    print("Sample width (bytes per sample):", self.sampwidth)
    print("Framerate (sampling rate):", self.framerate)
    print("Number of samples:", self.nframes)

########################################################################################################################
########################################################################################################################
########################################################################################################################