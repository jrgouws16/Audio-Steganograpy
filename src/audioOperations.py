# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 12:39:56 2019

@author: Johan Gouws
"""

import struct
import SignalsAndSlots

class stegoTools:

    def __init__(self, audio, name):
        self.audio = audio
        self.name = name
        self.nchannels, self.sampwidth, self.framerate, self.nframes, self.comptype,  self.compname = self.audio.getparams()
        self.samplesChannelOne = []
        self.samplesChannelTwo = []
        self.extractingSamples = SignalsAndSlots.SigSlot()

    def extractSamples(self):
        # Extract the samples from the audio file

        # Read frames and convert to sixteen bit sample decimal value
        format = '<{}h'.format(self.nchannels)

        for index in range(self.nframes):
            frame = self.audio.readframes(1)  # Read frame
            data = struct.unpack(format, frame)  # Unpack frame into sixteen bit sample

            self.samplesChannelOne.append(data[0])  # first (left) channel only

            if (self.samplesChannelOne[-1] == -32768):
                self.samplesChannelOne[-1] += 1

            if (self.nchannels == 2):
                self.samplesChannelTwo.append(data[1])
                if (self.samplesChannelTwo[-1] == -32768):
                    self.samplesChannelTwo[-1] += 1

            self.extractingSamples.trigger.emit((index+1) * 100 / self.nframes)

    def returnParameters(self):
        #Get input file parameters
        print("Channels:", self.nchannels)
        print("Sample width (bytes per sample):", self.sampwidth)
        print("Framerate (sampling rate):", self.framerate )
        print("Number of samples:", self.nframes)
        
    def returnSamplesChannelOne(self):
        return self.samplesChannelOne
    
    def returnSamplesChannelTwo(self):
        if (self.nchannels > 1):
            return self.samplesChannelTwo
        else:
            print("Audio is mono. Only one channel available")