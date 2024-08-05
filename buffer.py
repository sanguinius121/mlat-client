import numpy as np


class bufferClass: #buffer size = 259200 + 1440, buffer length = 1440
    def __init__(self,bufferSize,bufferLength):
        self.bufferSize = bufferSize
        self.bufferLength = bufferLength
        self.xBuff = np.zeros((bufferSize + bufferLength))
    def buffer(self, inputArray):
        # # Ensure input array has the correct size
        if inputArray.shape[0] != self.bufferSize:
            raise ValueError(f"Input array should have exactly {self.bufferSize} elements")

        # Buffer the last buffer_length elements of xBuff at the beginning
        self.xBuff[0:self.bufferLength] = self.xBuff[-self.bufferLength:]

        # Concatenate the input_matrix into the rest of xBuff
        self.xBuff[self.bufferLength:] = inputArray

        return self.xBuff
