import numpy as np

def config1090():
    symbolDuration = 1e-6
    chipsPerSymbol = 2
    longPacketDuration = 112e-6
    shortPacketDuration = 56e-6
    preambleDuration = 8e-6
    frontEndSampleRate = 12e6

    adsbParam = {}
    adsbParam['center_freq'] = 1090e6
    adsbParam['frontEndSampleRate'] = frontEndSampleRate
    adsbParam['delta_t'] = float(1/frontEndSampleRate)
    chipRate = chipsPerSymbol / symbolDuration
    n, d = np.round(frontEndSampleRate / chipRate).as_integer_ratio()
    if d > 2:
        interpRate = d
    else:
        if n <= 1:
            interpRate = 2 * d
        else:
            interpRate = d
    adsbParam['InterpolationFactor'] = interpRate
    sampleRate = frontEndSampleRate * interpRate
    adsbParam['SampleRate'] = sampleRate
    adsbParam['SamplesPerSymbol'] = int(sampleRate * symbolDuration)
    adsbParam['SamplesPerChip'] = adsbParam['SamplesPerSymbol'] // chipsPerSymbol
    adsbParam['MaxPacketLength'] = int((preambleDuration + longPacketDuration) * sampleRate)
    maxNumLongPacketsInFrame = 360
    maxPacketDuration = (preambleDuration + longPacketDuration)  # in seconds
    maxPacketLength = maxPacketDuration * frontEndSampleRate
    adsbParam['SamplesPerFrame'] = int(maxNumLongPacketsInFrame * maxPacketLength) #259200
    adsbParam['MaxNumPacketsInFrame'] = int(adsbParam['SamplesPerFrame'] // maxPacketLength // 4)
    print(adsbParam['MaxNumPacketsInFrame'])
    adsbParam['FrameDuration'] = adsbParam['SamplesPerFrame'] / frontEndSampleRate

    # Convert seconds to samples and bits
    adsbParam['LongPacketLength'] = int(longPacketDuration * sampleRate)
    adsbParam['PreambleLength'] = int(preambleDuration * sampleRate)
    adsbParam['LongPacketNumBits'] = int(longPacketDuration / symbolDuration)
    adsbParam['ShortPacketNumBits'] = int(shortPacketDuration / symbolDuration)

    #Preamble sequence
    adsbParam['SyncSequence'] = np.array([1,0,1,0,0,0,0,1,0,1,0,0,0,0,0,0])
    adsbParam['SyncSequenceLength'] = len(adsbParam['SyncSequence'])
    adsbParam['SyncSequenceHighIndices'] = np.where(adsbParam['SyncSequence'])[0] #find the position of 1 in SyncSequence
    adsbParam['SyncSequenceNumHighValues'] = len(adsbParam['SyncSequenceHighIndices'])
    adsbParam['SyncSequenceLowIndices'] = np.where(np.array(adsbParam['SyncSequence']) == 0)[0]  # find the position of 0 in SyncSequence
    adsbParam['SyncSequenceNumLowValues'] = len(adsbParam['SyncSequenceLowIndices'])
    ones_array = np.ones((adsbParam['SamplesPerChip'],1),'int')
    multiple_array = ones_array*adsbParam['SyncSequence']
    adsbParam['synchSignal'] = multiple_array.reshape(-1,order='F')
    adsbParam['synchDownSampleFactor'] = 2
    downSampledSynchSignal = adsbParam['synchSignal'][0::adsbParam['synchDownSampleFactor']]
    processedDownsampledSynch =downSampledSynchSignal*2 - 1 #0 to -1 and 1 to 1
    #flip the processed downsample synch sequence
    adsbParam['synchFilter'] = np.flipud(processedDownsampledSynch)
    return adsbParam