import numpy as np
from math import pi


def SOQPSK_TG_modulation(u, T, E, SPS):
    # (Standard) Ternary Precorder
    alpha = [0, 0] + [((-1)**k)*(2*u[k-1] - 1)*(u[k] - u[k-2]) for k in range(2, len(u))]

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
    for index in range(1, len(result)):
        phase[index] = phase[index-1] + result[index]

    # SOQPSK-TG signal baseband representation
    coefficient = complex(np.sqrt(E/T))
    signal = [coefficient * np.exp(1j * pi * (phase[i] + 0.25)) for i in range(len(phase))]

    return signal
