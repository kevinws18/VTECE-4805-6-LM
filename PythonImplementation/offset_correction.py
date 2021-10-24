from math import pi
import numpy as np


def calcOffsets(signal):
    unwrapped_signal = np.unwrap(np.angle(signal))
    cfo = (unwrapped_signal[-1] - unwrapped_signal[0]) / len(signal) / 6.27690
    po = (unwrapped_signal[0] - 0.791681) / -6.2832 - 0.00099

    return cfo, po


def correctOffsets(signal, cfo, po):
    corrected_signal = signal * np.exp(2j * pi * (-cfo * np.arange(len(signal)) + po))

    return corrected_signal
