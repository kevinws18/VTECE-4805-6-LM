from random import random
import numpy as np
import math, cmath
import matplotlib.pyplot as plt

# Parameters specific to SOQPSK-TG
T,  E, SPS = 1, 1, 20

# Random bitstream generation
number_of_bits = 1000
u = [0 if random() < 0.5 else 1 for _ in range(number_of_bits)]

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

# Eye diagram
eye_diagram(signal, 10, 40)

