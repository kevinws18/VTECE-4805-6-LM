import numpy as np
import math, cmath
from math import pi
import time
import pickle

class Modulator:
    def __init__(self) -> None:
        # Normalized Partial-Resposne Frequency Pulse
        data = open('PythonImplementation/procfTGs.txt','r')
        self.procfTGs = [float(i) for i in data.read().split('\n')]

    def SOQPSK_TG_modulation(self, data:bytearray, T=1, E=1, SPS=20):  
        
        # Generate an array of bits from a byte array
        number_of_bits = len(data) * 8
        u = [access_bit(data,i) for i in range(number_of_bits)]
        
        number_of_bits = len(u)

        # (Standard) Ternary Precorder
        # Soltuion to all 0s, all 1s, and alternating
        alpha = [0,0] + [((-1)**(k))*(2*u[k-1] - 1)*(u[k] - u[k-2]) for k in range(2, number_of_bits)]

        # Zero Padding
        padded = list(np.zeros(len(alpha) * int(SPS/2)))
        for index in range(len(alpha)):
            padded[index * int(SPS/2)] = alpha[index]

        # Filter Function
        length_padded, length_procfTGs, result = len(padded), len(self.procfTGs), list(np.zeros(len(padded)))
        for index in range(length_padded):
            sum = 0
            for index2 in range(length_procfTGs):
                if index - index2 >= 0:
                    sum = sum + self.procfTGs[index2] * padded[index - index2]
            result[index] = sum

        # Cumulative Sum
        phase = np.zeros(len(result))
        phase[0] = result[0]
        for index in range(1,len(result)):
            phase[index] = phase[index-1] + result[index]

        # SOQPSK-TG signal baseband representation
        coefficient = complex(math.sqrt(E/T))
        sig_cmplx = np.array([coefficient * cmath.exp(1j * math.pi * (phase[i] + 0.25)) for i in range(len(phase))])

        # f = open(f'tx_{time.strftime("%H_%M_%S")}.pkl', 'wb')
        # pickle.dump(sig_cmplx, f)

        # Convert to interleaved int12 values
        sig_int12 = np.empty(len(sig_cmplx)*2, dtype=np.int16)
        sig_int12[0::2] = 2047 * sig_cmplx.real
        sig_int12[1::2] = 2047 * sig_cmplx.imag
        return sig_int12


# Helper function for accessing a bit in a byte array
def access_bit(data: bytearray, num: int):
        base = int(num//8)
        shift = int(num%8)
        return (data[base] >> shift) & 0x01
