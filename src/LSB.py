# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 13:28:10 2019

@author: Johan Gouws
"""

import SignalsAndSlots

class LSB_encoding:
    # Constructor, initializing samples of message and cover, together with two signals
    def __init__(self, coverSamples, messageSamples):
        self.coverSamples = coverSamples
        self.messageSamples = messageSamples
        self.stegoSamples = []
        self.signalEmbedding = SignalsAndSlots.SigSlot()
        self.numberSamplesUsed = 0       # Samples used to embed secret message

    # Setter for the message samples    
    def setMessageSamples(self, messageSamples):
        self.messageSamples = messageSamples
            
    # Setter for the cover samples    
    def setCoverSamples(self, coverSamples):
        self.coverSamples = coverSamples
                
    # Function to place a single bit within a 16 bit cover sample
    def replaceBit(self, sample, LSB_number, bit):
        # Convert the sample to a sixteen bit binary string
        sample = "{0:016b}".format(sample)      
        
        # Convert binary string to a list
        sample = list(sample)                   
        
        # Replace the ith LSB with the bit
        sample[-1*LSB_number] = str(bit)        
        
        # Convert the list to a string
        sample = ''.join(sample)      

        # Return the decimal value  
        return int(sample,2)                    
        
    # Replaces LSB of each byte of the audio data by one bit from the text bit array
    def encode(self, LSB):
        self.numberSamplesUsed = 0
        
        # value to update the GUI
        progress = 0

        # For the length of the message, place the message bit in the cover sample and
        # update the GUI
        for i, bit in enumerate(self.messageSamples):
            self.stegoSamples.append(self.replaceBit(self.coverSamples[i], LSB , bit))
            self.numberSamplesUsed += 1
            progress += 1
            self.signalEmbedding.trigger.emit(float(progress)*100/len(self.coverSamples))

        # Write the remainder of the cover as if if the cover samples is more than the 
        # message bits and update the GUI
        while(len(self.stegoSamples) != len(self.coverSamples)):
            self.stegoSamples.append(self.coverSamples[len(self.stegoSamples)])
            progress += 1
            self.signalEmbedding.trigger.emit(float(progress) * 100 / len(self.coverSamples))
        
class LSB_decoding:
    # Slot for updating the GUI with progress of the decoding process
    def __init__(self, stegoSamples):
        self.stegoSamples = stegoSamples
        self.secretMessage = ''
        self.signalExtractingMessage = SignalsAndSlots.SigSlot()
        
    # Setter for the stego samples    
    def setStegoSamples(self, samples):
            self.stegoSamples = samples
            
    # Function to extract the ith bit of a sample
    def extractBit(self, sample, LSB_number):
        # Form a sixteen bit sample value string
        sample = "{0:016b}".format(sample)
        
        # Return the bit
        return sample[-1*LSB_number]                    

    # Extract LSB of each byte of the audio data by one bit from the text bit array
    def decode(self, messageBitLength, embeddingPosition):
        for i in range(messageBitLength):
            self.secretMessage += self.extractBit(self.stegoSamples[i], embeddingPosition)
            self.signalExtractingMessage.trigger.emit((i+1)*100/messageBitLength)

        return self.secretMessage

        