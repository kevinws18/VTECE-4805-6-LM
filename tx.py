# Class for transmitting a set of files

import time
import numpy as np
import pickle
from Packets_Py.PacketConstructor import DataPacketConstructor
from Packets_Py.MacPacket import HEADER_BYTE_COUNT, TRAILER_BYTE_COUNT
from PythonImplementation.modulation import Modulator
import SoapySDR
from SoapySDR import SOAPY_SDR_END_BURST, errToStr
from SoapySDR import SOAPY_SDR_TX, SOAPY_SDR_RX, SOAPY_SDR_CS12, SOAPY_SDR_CS16, SOAPY_SDR_CF32
import matplotlib.pyplot as plt

class TxController:
    def __init__(self, payload_size=1024, freq=2.412e9, bw=10e6, fs=31.15e6, gain=80) -> None:
        self.payload_size = payload_size
        self.packet_size = 1 + HEADER_BYTE_COUNT + payload_size + TRAILER_BYTE_COUNT + 1
        self.modulator = Modulator()
        self.setup_sdr(freq, bw, fs, gain)

    def setup_sdr(self, freq, bw, fs, gain):
        #Setup tx stream
        self.sdr = SoapySDR.Device(dict(driver='lime')) #create connection with SDR
        self.sdr.setSampleRate(SOAPY_SDR_TX, 0, fs)
        self.sdr.setFrequency(SOAPY_SDR_TX, 0, freq)
        self.sdr.setBandwidth(SOAPY_SDR_TX, 0, bw)
        self.sdr.setGain(SOAPY_SDR_TX, 0, gain)

        self.tx_stream = self.sdr.setupStream(SOAPY_SDR_TX, SOAPY_SDR_CS12, [0])

        #Setup rx stream
        self.sdr.setSampleRate(SOAPY_SDR_RX, 0, 1e6)
        self.sdr.setFrequency(SOAPY_SDR_RX, 0, 2.433e9)
        self.sdr.setBandwidth(SOAPY_SDR_RX, 0, 10e6)
        self.sdr.setGain(SOAPY_SDR_RX, 0, 20)
        self.rxStream = self.sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)

    def prepare_packets(self, filename):
        constructor = DataPacketConstructor(filename, self.payload_size)
        self.packets = constructor.make_packets()
        self.txbytes = constructor.make_bytearr()
        self.txbytes += b'\x00'

    def modulate_packets(self):
        self.signal = self.modulator.SOQPSK_TG_modulation(data=self.txbytes)

    def transmit_baseband(self):
        tx_buff = self.signal
        buff_len = len(tx_buff)//2
        
        self.sdr.activateStream(self.tx_stream)
        print('Now Transmitting')
        print(f'Sample rate: {self.sdr.getSampleRate(SOAPY_SDR_TX, 0)}')
        while True:
            try:
                num_packets = len(self.packets)
                samples_per_packet = buff_len//num_packets
                for i in range(0, buff_len, samples_per_packet):
                    rc = self.sdr.writeStream(self.tx_stream, [tx_buff], samples_per_packet)
                    if rc.ret != samples_per_packet:
                        print('TX Error {}: {}'.format(rc.ret, errToStr(rc.ret)))
                    rc = self.sdr.writeStream(self.tx_stream, [np.array([0]*(samples_per_packet*2))], samples_per_packet)
                    if rc.ret != samples_per_packet:
                        print('TX Error {}: {}'.format(rc.ret, errToStr(rc.ret)))
            except KeyboardInterrupt:
                 break

        # Stop streaming
        self.sdr.deactivateStream(self.tx_stream)
        self.sdr.closeStream(self.tx_stream)

    def wait_for_beacon(self):
       
        print("Waiting for Beacon Signal to Begin Transmission")
        self.sdr.activateStream(self.rxStream) #start streaming
        buff = np.array([0]*2040, np.complex64)

        while True:
            signal = np.array([], np.complex64)
            for i in range(20):
                sr = self.sdr.readStream(self.rxStream, [buff], len(buff))
                signal = np.append(signal, buff)

            if np.mean(np.abs(signal)) > 0.05:
                break

        self.sdr.deactivateStream(self.rxStream) #stop streaming
        self.sdr.closeStream(self.rxStream)

# Helper function for accessing a bit in a byte array
def access_bit(data: bytearray, num: int):
    base = int(num//8)
    shift = int(num%8)
    return (data[base] >> shift) & 0x01

if __name__ == '__main__':
    tx_controller = TxController(payload_size=15, fs=1e6)
    tx_controller.prepare_packets('Packets_Py/data.txt')
    # data = tx_controller.txbytes[0:tx_controller.packet_size]
    # print(data)
    # number_of_bits = len(data) * 8
    # u = [access_bit(data,i) for i in range(number_of_bits)]
    # print(u)
    # print(len(u))
    print(tx_controller.txbytes)
    tx_controller.modulate_packets()
    tx_controller.wait_for_beacon()
    tx_controller.transmit_baseband()