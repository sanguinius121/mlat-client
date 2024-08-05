from config1090 import config1090
from buffer import bufferClass
import numpy as np
from scipy.signal import convolve
from packetSearch import packetSearch
import adi
from decode import decode
import json
import socket
import pickle
import time

'''CONFIG CLIENT'''
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "100.104.228.105"
ADDR = (SERVER, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
def send(msg):
    message = pickle.dumps(msg)
    message_length = len(message)
    send_length = str(message_length).encode(FORMAT)
    send_length += b' '*(HEADER - len(send_length))
    decoded = send_length.decode(FORMAT)
    try:
        client.send(send_length)
        client.send(message)
    except Exception as err:
        print(f"An unexpected error occurred: {err}")  # Any other error


adsbParam = config1090()

'''CONFIG SDR'''
sdr_id = 'ip:192.168.1.173'
sdr = adi.Pluto(sdr_id)
sdr.gain_control_mode_chan0 = 'manual'
sdr.rx_hardwaregain_chan0 = 50.0 # dB
sdr.rx_lo = int(adsbParam['center_freq'])
sdr.sample_rate = int(adsbParam['frontEndSampleRate'])
sdr.rx_rf_bandwidth = int(adsbParam['frontEndSampleRate'])
sdr.rx_buffer_size = int(adsbParam['SamplesPerFrame'])

receiving_time = 0
while True:

    # testing_msg = {"Name" : "Tuan", "Age" : 30, "Job": None, "Married": True, "packet_id" : receiving_time}
    # send(testing_msg)

    epoch = time.time()
    try:
        samples = sdr.rx()
    except Exception as err:
        print(f"Error with sampling: {err}")  # Any other error
        continue
    zAbs = (np.abs(samples)) ** 2
    # fetching data into buffer
    bufferObj = bufferClass(adsbParam['SamplesPerFrame'] * adsbParam['InterpolationFactor'], \
                            adsbParam['MaxPacketLength'])
    bufferObj.buffer(zAbs)
    # decimate signal to save resources
    xBuffDownSampled = bufferObj.xBuff[0::adsbParam['synchDownSampleFactor']]
    vectorxBuff = np.linspace(0, len(xBuffDownSampled), len(xBuffDownSampled))

    crossCorr = convolve(np.array(xBuffDownSampled), np.array(adsbParam['synchFilter']), mode='full')

    pkt = packetSearch(crossCorr, bufferObj.xBuff, adsbParam, epoch)
    for packet in pkt:
        decoded_message = decode(packet, receiving_time, sdr_id)
        if decoded_message is not None:
            send(decoded_message)
    receiving_time = receiving_time + 1


#test decode header

send(DISCONNECT_MESSAGE)
client.close()
print("Connection closed!!!!!!!!!!!!!")