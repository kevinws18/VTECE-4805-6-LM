from random import random
import numpy as np
import math, cmath
import matplotlib.pyplot as plt

preamble = [0,0,1,1,0,1,1,0,0,0,0,0,0,0];

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

# Parameters specific to SOQPSK-TG
T,  E, SPS = 1, 1, 20

# Random bitstream generation
number_of_bits = 200
u = preamble + [0 if random() < 0.5 else 1 for _ in range(number_of_bits)]
#print(u)
#u = [0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1,1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1]
number_of_bits = len(u)
# (Standard) Ternary Precorder
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
coefficient = complex(math.sqrt(E/T))
signal = [coefficient * cmath.exp(1j * math.pi * (phase[i] + 0.25)) for i in range(len(phase))]

# Eye diagram plotter, use as an alternative to eyediagram()
def eye_diagram(signal, bits_per_symbol, n):
    fig = plt.figure()
    plt.subplot(2,1,1)
    plt.title('Eye Diagram for In-Phase Signal (I)')
    signal_graph = [num.real for num in signal]
    spacing = 2*bits_per_symbol
    for i in range(int(len(signal_graph)/spacing)-n):
        offset = i*spacing
        plt.plot(range(n), signal_graph[offset:offset+n])
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.xticks([0, math.floor(n/2), n], ['-0.5','0','0.5'])

    plt.subplot(2,1,2)
    signal_graph = [num.imag for num in signal]
    for i in range(int(len(signal_graph)/spacing)-n):
        offset = i*spacing
        plt.plot(range(n), signal_graph[offset:offset+n])
    plt.title('Eye Diagram for Quadrature Signal (Q)')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.xticks([0, math.floor(n/2), n], ['-0.5','0','0.5'])

    plt.show()
    bits = SOQPSK_TG_Demod(preamble, signal, 20)
    bitlen = range(len(bits))
    ulen = range(len(u))
    plt.scatter(bitlen, bits, edgecolors='blue')
    plt.scatter(ulen, u, marker='*')
    plt.show()
# Eye diagram
eye_diagram(signal, 10, 40)

