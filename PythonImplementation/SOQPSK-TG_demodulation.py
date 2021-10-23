from random import random
import numpy as np
import math, cmath
import matplotlib.pyplot as plt


def SOQPSK_TG_Demod(preamble, signal, SPS):
    samples_per_bit = SPS/2

    phase = (np.unwrap(np.angle(signal)) - 0.785416) / np.pi

    filtered = np.zeros(len(phase))
    for x in range(1, len(phase)-1, 1):
        filtered[x] = phase[x+1] - phase[x]

    filter_offset = 0.015
    padded = np.zeros(len(phase))
    for i in range(0, len(padded), 1):
        if(filtered[i] > filter_offset):
            padded[i] = 1
        elif(filtered[i] < -1 * filter_offset):
            padded[i] = -1

    alpha = np.zeros(int(len(padded)/samples_per_bit))
    for x in range(1, len(alpha) - 1, 1):
        alpha[x-1] = padded[(int((x-1) * samples_per_bit))]

    starter = [preamble[len(preamble) - 2], preamble[len(preamble) - 1]]
    bits = np.zeros(len(alpha))
    bits[0] = starter[0]
    bits[1] = starter[1]
    for x in range(2, len(alpha) - 1, 1):
        if((([1 if x%2 == 0 else -1][0]) * (2 * bits[x - 1] - 1) * (1- bits[x-2])) == alpha[x]):
            bits[x] = 1

    bits = bits[4:len(bits)]
    bits = np.append(bits,[0,0,0,0])
    return bits