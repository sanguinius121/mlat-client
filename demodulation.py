import numpy as np
from config1090 import config1090
def adsbDemod(in_samples, adsbParam):
    sps = adsbParam['SamplesPerSymbol']  # = 10
    spc = adsbParam['SamplesPerChip']  # = 5

    bit1 = np.concatenate((np.ones(spc), -np.ones(spc)))
    num_bits = in_samples.shape[0] // sps
    y_temp = np.reshape(in_samples, (num_bits, sps))
    y_soft = np.dot(y_temp, bit1)
    z = (y_soft > 0).astype(np.uint8)
    return z
