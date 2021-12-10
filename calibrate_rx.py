# AUTHOR: STEPHAN MULLER
# OWNER: VIRGINIA TECH/LOCKHEED MARTIN

# Run this module once calibrate_tx.py is running on the opposite lime device

import SoapySDR
from SoapySDR import SOAPY_SDR_RX
from SoapySDR import SOAPY_SDR_CF32 #SOAPY_SDR_ constants
import numpy as np#use numpy for buffers
import matplotlib.pyplot as plt
from PythonImplementation.offset_correction import *
import pickle
import time

args = dict(driver="lime")
sdr = SoapySDR.Device(args)

sdr.setSampleRate(SOAPY_SDR_RX, 0, 1e6)
sdr.setFrequency(SOAPY_SDR_RX, 0, 2.412e9)
sdr.setBandwidth(SOAPY_SDR_RX, 0, 10e6)
sdr.setGain(SOAPY_SDR_RX, 0, 20)

#setup a stream (complex floats)
rxStream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)

sdr.activateStream(rxStream) #start streaming
buff = np.array([0]*2040, np.complex64)
signal = np.array([], np.complex64)

for i in range(1):
    sr = sdr.readStream(rxStream, [buff], len(buff))
    signal = np.append(signal, buff)
sdr.deactivateStream(rxStream) #stop streaming
sdr.closeStream(rxStream)

(cfo, po) = calcOffsets(signal)
print(f'cfo: {cfo}, po: {po}')
with open('cfo.bin', 'wb') as f:
    pickle.dump((cfo, po), f)

# plt.plot(np.real(signal))
# plt.plot(np.imag(signal))
# plt.show()