import numpy as np
from math import pi


def mod(u, T, E, SPS):
    # Random bitstream generation
    number_of_bits = len(u)

    # (Standard) Ternary Precorder
    # Soltuion to all 0s, all 1s, and alternating
    alpha = [0,0] + [((-1)**(k))*(2*u[k-1] - 1)*(u[k] - u[k-2]) for k in range(2, number_of_bits)]

    # Normalized Partial-Resposne Frequency Pulse
    data = open('procfTGs.txt','r')
    procfTGs = [float(i) for i in data.read().split('\n')]

    # Zero Padding
    padded = list(np.zeros(len(alpha) * int(SPS/2)))
    for index in range(len(alpha)):
        padded[index * int(SPS/2)] = alpha[index]

    # Filter Function
    length_padded, length_procfTGs, result = len(padded), len(procfTGs), list(np.zeros(len(padded)))
    for index in range(length_padded):
        sum = 0
        for index2 in range(length_procfTGs):
            if index - index2 >= 0:
                sum = sum + procfTGs[index2] * padded[index - index2]
        result[index] = sum

    # Cumulative Sum
    phase = np.zeros(len(result))
    phase[0] = result[0]
    for index in range(1,len(result)):
        phase[index] = phase[index-1] + result[index]

    # SOQPSK-TG signal baseband representation
    coefficient = complex(np.sqrt(E/T))
    return [coefficient * np.exp(1j * np.pi * (phase[i] + 0.25)) for i in range(len(phase))]


def calcOffsets(signal):
    unwrapped_signal = np.unwrap(np.angle(signal))
    cfo = (unwrapped_signal[-1] - unwrapped_signal[0]) / len(signal) / 6.27690
    po = (unwrapped_signal[0] - 0.791681) / -6.2832 - 0.00099

    return cfo, po


def correctOffsets(signal, cfo, po):
    corrected_signal = signal * np.exp(2j * pi * (-cfo * np.arange(len(signal)) + po))

    return corrected_signal


def demod(preamble, signal, SPS):
    samples_per_bit = SPS/2

    phase = (np.unwrap(np.angle(signal)) - 0.785416) / np.pi
    filtered = [0] + [phase[i+1] - phase[i] for i in range(1, len(phase)-1)] + [0]

    filter_offset = 0.017
    padded = [1 if filtered[i] > filter_offset else -1 if filtered[i] < -filter_offset else 0 for i in range(len(phase))]
    alpha = [padded[int(i * samples_per_bit)-1] for i in range(int(len(padded) / samples_per_bit))]

    bits = preamble[-2:]
    for i in range(2, len(alpha)):
        bits.append(int(((1 if (i%2 == 0) else -1) * (2*bits[i-1] - 1) * (1 - bits[i-2])) == alpha[i]))

    bits = bits[4:] + [0, 0, 0, 0]
    return bits
