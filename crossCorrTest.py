import numpy as np
import matplotlib.pyplot as plt
from config1090 import config1090
from scipy.signal import convolve
adsbParam = config1090()

#packet parammeter
spc = adsbParam['SamplesPerChip']
syncLen = adsbParam['SyncSequenceLength']
syncSigLen = syncLen * spc #96
packetCnt = 0

subFrameLen = syncSigLen
subFrameDownLen = int(subFrameLen // adsbParam['synchDownSampleFactor'])
numSubFrames = 4
#initialize the return values
packetSamples = np.zeros((numSubFrames,syncSigLen))

# Define the signals
signal = np.array([1, 2, 1, 2, 2, 1, 2, 1, 2, 1, 0, 2, 1, 1, 0 , 1,\
                    10,10,10,10,10,10, 2,0,1,0,1,2, 10,10,10,10,10,10, 2,2,2,1,0,1, 2,2,2,1,0,1, 1,2,2,1,0,1, 0,2,2,1,0,1,\
                    10,10,10,10,10,10, 0,2,1,2,2,0, 10,10,10,10,10,10, 2,1,2,2,2,1, 2,2,2,1,2,2, 2,1,2,2,2,1, 2,2,2,1,2,2, 2,2,2,1,2,2, 2,2,2,1,2,2, \
                    10, 10, 2, 10, 2, 1, 1, 2, 1, 2, 10, 2, 1, 2, 10, 1, 2, 1, 10, 1, 10, 10, 1, 1, 0 , 1, 1, 1, 0, 0, 1, 0, 2, 2, 2, 1, 0, 2, 0, 1, \
                    2, 1, 1, 2, 1, 1, 1, 1, 0, 1, 2, 2, 0, 1, 2, 1, \
                   10,10,10,10,10,10, 2,0,1,0,1,2, 10,10,10,10,10,10, 2,2,2,1,0,1, 2,2,2,1,0,1, 1,2,2,1,0,1, 0,2,2,1,0,1, \
                   10,10,10,10,10,10, 0,2,1,2,2,0, 10,10,10,10,10,10, 2,1,2,2,2,1, 2,2,2,1,2,2, 2,1,2,2,2,1, 2,2,2,1,2,2, 2,2,2,1,2,2, 2,2,2,1,2,2, \
                   13, 2, 9, 2, 2, 2, 1, 10, 2, 12, 2, 2, 1, 2, 2, 2, 10, 1, 0, 0, 1, 10, 2, 2, 2, 10, 0, 10, 10, 1, 2, 0,\
                   2,1,1,2,2,1,2,1,2,2,2,1,2,2,2,1,1,2,2,1,2,2]) # len = 112

signalDownsampled = signal[0::adsbParam['synchDownSampleFactor']]

# # Compute the cross-correlation between the two signals
crossCorr = convolve(signalDownsampled, adsbParam['synchFilter'],mode='full')
for p in range(numSubFrames-1):
    #calculate start and stop points and find max indices
    startIndex = p*subFrameDownLen
    stopIndex  = startIndex + subFrameDownLen
    maxIndices = startIndex + np.argmax(crossCorr[startIndex:stopIndex]) #absolute indices
    #remove filter delay
    synchIndices = (maxIndices - len(adsbParam['synchFilter']) + 1)*adsbParam['synchDownSampleFactor']
    if synchIndices > 0 and (synchIndices < (len(signal) - subFrameLen)):
        rxSynchSequence = signal[synchIndices:(synchIndices + subFrameLen)]
        rxSynchSequenceReshaped = np.reshape(rxSynchSequence,(adsbParam['SyncSequenceLength'],spc))
        rxSynchSequenceAdded = np.sum(rxSynchSequenceReshaped,axis=1)
        highValue = np.sum(rxSynchSequenceAdded[adsbParam['SyncSequenceHighIndices']])/adsbParam['SyncSequenceNumHighValues']
        lowValue = np.sum(rxSynchSequenceAdded[adsbParam['SyncSequenceLowIndices']])/adsbParam['SyncSequenceNumLowValues']
        threshHold = (highValue+lowValue)/2
        if np.all(np.logical_xor(rxSynchSequenceAdded < threshHold, adsbParam['SyncSequence'])):
            packetCnt = packetCnt + 1
            if packetCnt < numSubFrames:
                packetSamples[(packetCnt-1),:] = signal[synchIndices:(synchIndices+subFrameLen)]
print(packetSamples)

#REMOVE FILTER DELAYING
#synchIndex =

#Print the result

plt.subplot(2,1,1)
plt.stem(signal)
plt.grid(True)
#
plt.subplot(2,1,2)
plt.stem(crossCorr)
plt.grid(True)
#
plt.show()
