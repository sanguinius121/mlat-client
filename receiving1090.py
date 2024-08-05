from config1090 import config1090
from buffer import bufferClass
import numpy as np
from scipy.signal import convolve
from packetSearch import packetSearch
import adi
from decode import decode
import json


adsbParam = config1090()

#config SDR
sdr = adi.Pluto('ip:192.168.2.1')
sdr.gain_control_mode_chan0 = 'manual'
sdr.rx_hardwaregain_chan0 = 50.0 # dB
sdr.rx_lo = int(adsbParam['center_freq'])
sdr.sample_rate = int(adsbParam['frontEndSampleRate'])
sdr.rx_rf_bandwidth = int(adsbParam['frontEndSampleRate'])
sdr.rx_buffer_size = int(adsbParam['SamplesPerFrame'])
receiving_time = 0
with open('mt1_receiving_7.txt', 'w') as file:
    while receiving_time < 100:
        samples = sdr.rx()
        zAbs = (np.abs(samples))**2
        #fetching data into buffer
        bufferObj = bufferClass(adsbParam['SamplesPerFrame']*adsbParam['InterpolationFactor'],\
                                adsbParam['MaxPacketLength'])
        bufferObj.buffer(zAbs)
        #decimate signal to save resources
        xBuffDownSampled = bufferObj.xBuff[0::adsbParam['synchDownSampleFactor']]
        vectorxBuff = np.linspace(0,len(xBuffDownSampled),len(xBuffDownSampled))

        crossCorr = convolve(np.array(xBuffDownSampled),np.array(adsbParam['synchFilter']),mode='full')

        pkt = packetSearch(crossCorr,bufferObj.xBuff,adsbParam)
        for packet in pkt:
            decoded_message = decode(packet, receiving_time)
            if decoded_message is not None:
                json_message = json.dumps(decoded_message)
                file.writelines(json_message + '\n')
        receiving_time = receiving_time + 1
file.close()
