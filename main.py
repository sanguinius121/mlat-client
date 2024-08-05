from config1090 import config1090
from buffer import bufferClass
import numpy as np
import scipy.io
from scipy.signal import convolve
from packetSearch import packetSearch
from decode import decode
import json



adsbParam = config1090()
#reading .mat file
matContents = scipy.io.loadmat('1090_caichien_8.mat')
iq_samples = matContents['iq_samples']


with open('data_caichien8.txt', 'w') as file:
    for packet in range(4):
        z = np.ravel(iq_samples[packet*adsbParam['SamplesPerFrame']:(packet+1)*adsbParam['SamplesPerFrame']])
        zAbs = (np.abs(z))**2

        #fetching data into buffer
        bufferObj = bufferClass(adsbParam['SamplesPerFrame']*adsbParam['InterpolationFactor'],\
                                adsbParam['MaxPacketLength'])
        bufferObj.buffer(zAbs)
        xBuffDownSampled = bufferObj.xBuff[0::adsbParam['synchDownSampleFactor']]
        vectorxBuff = np.linspace(0,len(xBuffDownSampled),len(xBuffDownSampled))

        # # cross correlation the preamble and buffered signal
        crossCorr = convolve(np.array(xBuffDownSampled),np.array(adsbParam['synchFilter']),mode='full')

        messages = packetSearch(crossCorr,bufferObj.xBuff,adsbParam)
        #print (pkt)
        for message in messages:
            decoded_message = decode(message, packet)
            if decoded_message is not None:
                json_message = json.dumps(decoded_message)
                file.writelines(json_message + '\n')
            else:
                continue
file.close()
# json_string = json.dumps(decoded)
# print(json_string)
'''
end here 
Status:
    - Have a list of decoded objects
    - Need to classify and process
'''

