# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 13:28:10 2019

@author: Johan Gouws
"""

import wave
import struct
import SignalsAndSlots

class LSB_encoding:

    def __init__(self, coverSamples, messageSamples):
        self.coverSamples = coverSamples
        self.messageSamples = messageSamples
        self.stegoSamples = []
        self.signalWriting = SignalsAndSlots.SigSlot()
        self.signalEmbedding = SignalsAndSlots.SigSlot()

    def setMessageSamples(self, messageSamples):
        if(len(messageSamples) > len(self.coverSamples) and len(self.coverSamples) != 0):
            print("Please enter a message with samples equal or smaller than the cover file samples")
        
        else:    
            self.messageSamples = messageSamples
            
    def setCoverSamples(self, coverSamples):
        if(len(coverSamples) < len(self.messageSamples) and len(self.messageSamples) != 0):
            print("Please enter a cover file of sufficient length for the message to be embedded")
        
        else:    
            self.coverSamples = coverSamples
                
    def replaceBit(self, sample, LSB_number, bit):
        sample = "{0:016b}".format(sample)
        sample = list(sample)                   # Convert binary string to a list
        sample[-1*LSB_number] = str(bit)        # Replace the ith LSB with the bit
        sample = ''.join(sample)                # Convert the list to a string
        return int(sample,2)                    # Return the decimal value
        
    def encode(self, LSB):
        # Replace LSB of each byte of the audio data by one bit from the text bit array
        progress = 0

        for i, bit in enumerate(self.messageSamples):
            self.stegoSamples.append(self.replaceBit(self.coverSamples[i], LSB , bit))
            progress += 1
            self.signalEmbedding.trigger.emit(float(progress)*100/len(self.coverSamples))
            
        while(len(self.stegoSamples) != len(self.coverSamples)):
            self.stegoSamples.append(self.coverSamples[len(self.stegoSamples)])
            progress += 1
            self.signalEmbedding.trigger.emit(float(progress) * 100 / len(self.coverSamples))
            
    def writeStegoToFile(self, fileName, parameters):
        with wave.open(fileName, 'wb') as fd:
            fd.setparams(parameters)
        
            for i in range(len(self.stegoSamples)):
                # print(self.stegoSamples[i])
                fd.writeframes(struct.pack('<h', self.stegoSamples[i]))
                self.signalWriting.trigger.emit((i+1)*100/(len(self.stegoSamples)))
            
        fd.close()

        
class LSB_decoding:

    def __init__(self, stegoSamples):
        self.stegoSamples = stegoSamples
        self.secretMessage = ''
        self.signalExtractingMessage = SignalsAndSlots.SigSlot()
        
    def setStegoSamples(self, samples):
            self.stegoSamples = samples
            
    # Function to replace the ith bit of a sample
    def extractBit(self, sample, LSB_number):
        sample = "{0:016b}".format(sample)
        return sample[-1*LSB_number]                    # Return the decimal value

    def decode(self, messageBitLength, embeddingPosition):
        # Extract LSB of each byte of the audio data by one bit from the text bit array
        for i in range(messageBitLength):
            self.secretMessage += self.extractBit(self.stegoSamples[i], embeddingPosition)
            self.signalExtractingMessage.trigger.emit((i+1)*100/messageBitLength)

        return self.secretMessage

        