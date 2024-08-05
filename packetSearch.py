from config1090 import config1090
import numpy as np
from demodulation import adsbDemod
from parseHeader import parseHeader
from bin2hex import helper_adsb_bin2hex

def packetSearch(crossCorr, xBuff,adsbParam, epoch):  #''''''
    packetCnt = 0
    pkt = [] # a list of libraries which keys are hexStr and indice
    spc = adsbParam['SamplesPerChip'] # 5 or 6
    syncLen = adsbParam['SyncSequenceLength'] # = 16
    syncSigLen = syncLen * spc  # 96
    subFrameLen = adsbParam['MaxPacketLength'] # 120
    subFrameDownLen = subFrameLen//adsbParam['synchDownSampleFactor']
    numSubFrames = len(xBuff)//subFrameLen
    packetSamples = np.zeros((adsbParam['MaxNumPacketsInFrame'], adsbParam['LongPacketLength']))
    for p in range(numSubFrames-1):
        startIndex = p * subFrameDownLen
        stopIndex = startIndex + subFrameDownLen
        #find the indices where max values are in the cossCorr
        maxIndices = startIndex + np.argmax(crossCorr[startIndex:stopIndex])
        #remove delaying caused by convolution, find the start of preamble
        synchIndices = (maxIndices - len(adsbParam['synchFilter']) + 1) * adsbParam['synchDownSampleFactor']
        if synchIndices > 0 and (synchIndices < (len(xBuff) - subFrameLen)):
            rxSynchSequence = xBuff[synchIndices:(synchIndices+syncSigLen)]
            rxSynchSequenceReshaped = np.reshape(rxSynchSequence, (adsbParam['SyncSequenceLength'],spc))
            rxSynchSequenceAdded = np.sum(rxSynchSequenceReshaped, axis=1)
            highValue = np.sum(rxSynchSequenceAdded[adsbParam['SyncSequenceHighIndices']])\
                        / adsbParam['SyncSequenceNumHighValues']
            lowValue = np.sum(rxSynchSequenceAdded[adsbParam['SyncSequenceLowIndices']])\
                       / adsbParam['SyncSequenceNumLowValues']
            threshHold = (highValue + lowValue) * 0.5
            if np.all(np.logical_xor(rxSynchSequenceAdded < threshHold, adsbParam['SyncSequence'])):
                packetCnt = packetCnt + 1
                if packetCnt < adsbParam['MaxNumPacketsInFrame']:
                    new_pkt = {}
                    new_pkt['indice'] = int(synchIndices)           #*adsbParam['delta_t'] + epoch_time
                    new_pkt['epoch'] = int(synchIndices)*adsbParam['delta_t'] + epoch
                    samples = xBuff[(synchIndices+syncSigLen):(synchIndices + subFrameLen)]
                    bin = adsbDemod(samples, adsbParam)
                    df, ca = parseHeader(bin)
                    if df in [0, 4, 5, 11]:
                        bin = bin[0:56]
                    elif df in [16, 17, 18, 19, 20, 21, 24]:
                        bin = bin
                    else:
                        bin = None
                    hexStr = helper_adsb_bin2hex(bin)
                    if hexStr is not None:
                        new_pkt['hexStr'] = hexStr
                        pkt.append(new_pkt)
    return pkt



#
# def packetSearch(crossCorr, xBuff,adsbParam):  #''''''
#     packetCnt = 0
#     synchIndicesArray = []
#     spc = adsbParam['SamplesPerChip'] # 5 or 6
#     syncLen = adsbParam['SyncSequenceLength'] # = 16
#     syncSigLen = syncLen * spc  # 96
#     subFrameLen = adsbParam['MaxPacketLength'] # 120
#     subFrameDownLen = subFrameLen//adsbParam['synchDownSampleFactor']
#     numSubFrames = len(xBuff)//subFrameLen
#     packetSamples = np.zeros((adsbParam['MaxNumPacketsInFrame'], adsbParam['LongPacketLength']))
#     for p in range(numSubFrames-1):
#         startIndex = p * subFrameDownLen
#         stopIndex = startIndex + subFrameDownLen
#         #find the indices where max values are in the cossCorr
#         maxIndices = startIndex + np.argmax(crossCorr[startIndex:stopIndex])
#         #remove delaying caused by convolution, find the start of preamble
#         synchIndices = (maxIndices - len(adsbParam['synchFilter']) + 1) * adsbParam['synchDownSampleFactor']
#         if synchIndices > 0 and (synchIndices < (len(xBuff) - subFrameLen)):
#             rxSynchSequence = xBuff[synchIndices:(synchIndices+syncSigLen)]
#             rxSynchSequenceReshaped = np.reshape(rxSynchSequence, (adsbParam['SyncSequenceLength'],spc))
#             rxSynchSequenceAdded = np.sum(rxSynchSequenceReshaped, axis=1)
#             highValue = np.sum(rxSynchSequenceAdded[adsbParam['SyncSequenceHighIndices']])\
#                         / adsbParam['SyncSequenceNumHighValues']
#             lowValue = np.sum(rxSynchSequenceAdded[adsbParam['SyncSequenceLowIndices']])\
#                        / adsbParam['SyncSequenceNumLowValues']
#             threshHold = (highValue + lowValue) * 0.5
#             if np.all(np.logical_xor(rxSynchSequenceAdded < threshHold, adsbParam['SyncSequence'])):
#                 packetCnt = packetCnt + 1
#                 synchIndicesArray.append(synchIndices)
#                 if packetCnt < adsbParam['MaxNumPacketsInFrame']:
#                     packetSamples[(packetCnt - 1), :] = xBuff[(synchIndices+syncSigLen):(synchIndices + subFrameLen)]
#     return packetSamples, synchIndicesArray, packetCnt