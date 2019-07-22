import sys
import SignalsAndSlots

class MessageFileEncoding:
    def __init__(self, messageFile):
        try:
            self.messageFilePath = 'C:/Users/project/Desktop/EPR practical/Media/' + messageFile
            self.fileObject = open(self.messageFilePath, 'rb')
            self.messageLength = len(self.fileObject.read())
            self.fileObject = open(self.messageFilePath, 'rb')
            self.signalMessage = SignalsAndSlots.SigSlot()
        except:
            SignalsAndSlots.showErrorMessage('Error in opening message file', 'Message file does not exist or entered incorrectly')

    def returnMessageSamples(self):
        totalSamples = ''
        totalBytes = 0
        while (1):
            byte = self.fileObject.read(1)
            totalBytes += 1
            self.signalMessage.trigger.emit((totalBytes+1)*100/self.messageLength)
            if (len(byte) == 0):
                break
            sample = "{0:08b}".format(int.from_bytes(byte, byteorder=sys.byteorder))
            totalSamples += sample

        return list(map(int, totalSamples))

    def messageToBinary(self, message):
        # Convert the string to binary sequence
        # Convert the binary sequence into a binary list
        return list(map(int, ''.join('{0:08b}'.format(ord(x), 'b') for x in message)))

    def __del__(self):
        self.fileObject.close()


class MessageFileDecoding:
    def __init__(self, messageFile):
        self.messageFilePath = 'C:/Users/project/Desktop/EPR practical/Media_decoded/' + messageFile
        self.fileObject = open(self.messageFilePath, 'wb')
        self.signalWriteMessage = SignalsAndSlots.SigSlot()

    def writeTotalSamplesToFile(self, samples):
        originalSize = len(samples)
        while (len(samples) > 0):
            self.fileObject.write((int(samples[0:8], 2).to_bytes(1, byteorder=sys.byteorder)))
            samples = samples[8:]
            self.signalWriteMessage.trigger.emit(100-100.0*len(samples)/originalSize)

    def __del__(self):
        self.fileObject.close()

