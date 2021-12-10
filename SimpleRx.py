# AUTHOR: STEPHAN MULLER
# OWNER: VIRGINIA TECH/LOCKHEED MARTIN

# This script provides retrieves a packet burst from a received signal,
# and plots the retrieved signal against the expected signal.
# The binary bits are also reconstructed and BER calculated.

import SoapySDR
from SoapySDR import *
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_TX
from SoapySDR import SOAPY_SDR_CF32, SOAPY_SDR_CS12 #SOAPY_SDR_ constants
from PythonImplementation.offset_correction import *
from PythonImplementation.demodulation import SOQPSK_TG_Demodulation
import numpy #use numpy for buffers
import matplotlib.pyplot as plt
import pickle
import time


#create device instance
args = dict(driver="lime")
sdr = SoapySDR.Device(args)

tx_signal = pickle.load( open( "tx_sample.pkl", "rb" ) )
tx_signal = tx_signal[:2150]
tx_bits = np.array([0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1])

#apply settings
sdr.setSampleRate(SOAPY_SDR_RX, 0, 1e6)
sdr.setFrequency(SOAPY_SDR_RX, 0, 2.412e9)
sdr.setBandwidth(SOAPY_SDR_RX, 0, 10e6)
sdr.setGain(SOAPY_SDR_RX, 0, 20)

#Get the calibration values
with open('cfo.bin', 'rb') as f:
    (cfo, po) = pickle.load(f)

#setup a stream (complex floats)
rxStream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)

#Send the beacon signal
sdr.setSampleRate(SOAPY_SDR_TX, 0, 1e6)
sdr.setFrequency(SOAPY_SDR_TX, 0, 2.433e9)
sdr.setBandwidth(SOAPY_SDR_TX, 0, 10e6)
sdr.setGain(SOAPY_SDR_TX, 0, 80)

tx_stream = sdr.setupStream(SOAPY_SDR_TX, SOAPY_SDR_CS12, [0])

samps = np.ones(4080)

print("Now Transmitting Beacon Signal")
for i in range(20):
    sdr.writeStream(tx_stream, [samps], len(samps)//2)

sdr.deactivateStream(tx_stream)
sdr.closeStream(tx_stream)

while True:
    try:
        sdr.activateStream(rxStream) #start streaming

        #create a re-usable buffer for rx samples
        buff = numpy.array([0]*2040, numpy.complex64)
        signal = numpy.array([], numpy.complex64)

        # #receive some samples
        for i in range(5):
            sr = sdr.readStream(rxStream, [buff], len(buff))
            signal = numpy.append(signal, buff)
        print("received samples")
        sdr.deactivateStream(rxStream) #stop streaming

        # Isolate the packet burst from the rest of the signal
        if numpy.all(numpy.abs(signal[:100]) < numpy.mean(numpy.abs(signal))):
            burst = signal[:4300]
        else:
            continue
        mask = numpy.abs(burst) > numpy.mean(numpy.abs(burst))
        packet_signal = burst[mask]

        # cfo, po = (-0.00034885869783658665, -0.16736500180947983)
        packet_signal = correctOffsets(packet_signal, cfo, po)

        bits = SOQPSK_TG_Demodulation([0,0,1,0,1,1,0,0], packet_signal)[:-4]

        errors = np.abs(np.matrix(bits) - np.matrix(tx_bits[:len(bits)]))
        num_errors = np.sum(errors)
        ber = np.sum(errors)/len(bits)

        print(f'Bit Errors:{np.sum(errors)}')
        print(f'Bit Error Rate: {np.sum(errors)/len(bits)}')

        plt.figure(figsize=(13, 7))
        sub = plt.subplot(2,2,1)
        plt.plot(range(len(tx_signal)), np.real(tx_signal))
        plt.plot(range(len(tx_signal)), np.imag(tx_signal))
        plt.title('Transmitted baseband signal')
        plt.legend(['real', 'imaginary'], loc='upper center', bbox_to_anchor=(0.5, 1.05),
                ncol=3, fancybox=True, shadow=True)
        plt.xlim((0,len(packet_signal)+1))

        sub = plt.subplot(2,2,3)
        plt.plot(range(len(packet_signal)), np.real(packet_signal))
        plt.plot(range(len(packet_signal)), np.imag(packet_signal))
        plt.title('Received baseband signal')
        plt.legend(['real', 'imaginary'], loc='upper center', bbox_to_anchor=(0.5, 1.05),
                ncol=3, fancybox=True, shadow=True)
        plt.xlim((0,len(packet_signal)+1))

        sub = plt.subplot(2,2,2)
        plt.plot(tx_bits,'o')
        plt.plot(bits, '*')
        plt.title('Original vs Demodulated bits')
        sub.legend(['Original', 'Demodulated'], loc='upper center', bbox_to_anchor=(0.5, 1.05),
                ncol=3, fancybox=True, shadow=True)
        plt.xlim((-1,len(bits)))
        plt.ylim(top=1.15)

        sub = plt.subplot(2,2,4)
        plt.text(0.3,0.5,'Bit Errors: ' + str(num_errors) + '\nBit Error Rate: ' + str(ber))


        plt.show()

        time.sleep(5) #loops and grabs new samples every 5 seconds
    except KeyboardInterrupt:
        break

#shutdown the stream
sdr.deactivateStream(rxStream) #stop streaming
sdr.closeStream(rxStream)

del sdr