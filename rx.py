# AUTHOR: STEPHAN MULLER
# OWNER: VIRGINIA TECH/LOCKHEED MARTIN

# RX Module

# This class provides the framework for generating a fully reliable
# transmission system. The VTECE-4805-6-LM project's conclusion was
# reached once binary bits were recovered from the received signal.
# Next steps are to decode the FEC encoding, and restructure the packets.
# Please view test_packets.py to show an example of packet reconstruction.

import SoapySDR
from SoapySDR import SOAPY_SDR_RX
from SoapySDR import SOAPY_SDR_CF32 #SOAPY_SDR_ constants
import numpy as np #use numpy for buffers
import matplotlib.pyplot as plt
import pickle
import time

class RxController:
    def __init__(self, payload_size=1024, freq=2.412e9, bw=10e6, fs=1e6, gain=30) -> None:
        self.setup_sdr(freq, bw, fs, gain)
        self.rx_buffer = np.array([0]*10200, np.complex64)
        self.signal = np.array([], dtype=np.complex64)

    def setup_sdr(self, freq, bw, fs, gain):
        self.sdr = SoapySDR.Device(dict(driver='lime')) #create connection with SDR
        self.sdr.setSampleRate(SOAPY_SDR_RX, 0, fs)
        self.sdr.setFrequency(SOAPY_SDR_RX, 0, freq)
        self.sdr.setBandwidth(SOAPY_SDR_RX, 0, bw)
        self.sdr.setGain(SOAPY_SDR_RX, 0, gain)

        self.rx_stream = self.sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)

    def receive(self):
        self.sdr.activateStream(self.rx_stream)

        try:
            received = False
            receiving = False
            while not received:
                sr = self.sdr.readStream(self.rx_stream, [self.rx_buffer], len(self.rx_buffer))
                if np.mean(np.abs(self.rx_buffer)) > .05:
                    receiving = True
                    self.signal = np.append(self.signal, self.rx_buffer)
                elif receiving:
                    received = True

            print("finished receiving")
            # f = open(f'rx_{time.strftime("%H_%M_%S")}.pkl', 'wb')
            # pickle.dump(self.signal, f)
            # self.signal = np.array([], dtype=np.complex64)
        except KeyboardInterrupt: 
            pass

        plt.plot(np.real(self.signal[:10000]), label="I")
        plt.plot(np.imag(self.signal[:10000]), label="Q")
        plt.legend()
        plt.title("I/Q Rx Samples Received")
        plt.show()

        self.sdr.deactivateStream(self.rx_stream) #stop streaming
        self.sdr.closeStream(self.rx_stream)

if __name__ == '__main__':
    rx_controller = RxController(payload_size=15)
    rx_controller.receive()