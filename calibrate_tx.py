# AUTHOR: STEPHAN MULLER
# OWNER: VIRGINIA TECH/LOCKHEED MARTIN

# Run this module to transmit a 0-sigmal in baseband.
# On the opposite LimeSDR device, run calibrate_rx to calculate
# frequency and phase offset values and store them
# NOTE: this pair of script should be run every time the physical environment changes significantly

# Once calibrations is complete, this script can be safely terminated with CTRL-C

import time
import numpy as np
import pickle
from Packets_Py.PacketConstructor import DataPacketConstructor
from Packets_Py.MacPacket import HEADER_BYTE_COUNT, TRAILER_BYTE_COUNT
from PythonImplementation.modulation import Modulator
import SoapySDR
from SoapySDR import SOAPY_SDR_END_BURST, errToStr
from SoapySDR import SOAPY_SDR_TX, SOAPY_SDR_CS12, SOAPY_SDR_CS16

sdr = SoapySDR.Device(dict(driver='lime')) #create connection with SDR
sdr.setSampleRate(SOAPY_SDR_TX, 0, 1e6)
sdr.setFrequency(SOAPY_SDR_TX, 0, 2.412e9)
sdr.setBandwidth(SOAPY_SDR_TX, 0, 10e6)
sdr.setGain(SOAPY_SDR_TX, 0, 80)

tx_stream = sdr.setupStream(SOAPY_SDR_TX, SOAPY_SDR_CS12, [0])
sdr.activateStream(tx_stream)

samps = np.zeros(4080)

print("Now Transmitting Calibration Signal")
while True:
    try:
        sdr.writeStream(tx_stream, [samps], len(samps)//2)
    except KeyboardInterrupt:
        break

sdr.deactivateStream(tx_stream)
sdr.closeStream(tx_stream)