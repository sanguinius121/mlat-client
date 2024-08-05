import adi
import numpy as np
import matplotlib.pyplot as plt


sdr = adi.Pluto('ip:192.168.1.173')
sdr.gain_control_mode_chan0 = 'manual'
sdr.rx_hardwaregain_chan0 = 50.0 # dB
sdr.rx_lo = int(1090e6)
sdr.sample_rate = int(12e6)
sdr.rx_rf_bandwidth = int(sdr.sample_rate)
sdr.rx_buffer_size = int(1e6)

samples = sdr.rx()
zAbs = (np.abs(samples))**2

vector = np.linspace(0,len(zAbs),len(zAbs) )

plt.plot(vector,zAbs)
plt.show()
