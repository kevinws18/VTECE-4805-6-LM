import numpy as np
import math, cmath
import matplotlib.pyplot as plt

T, E, SPS = 1, 1, 20

def SOQPSK_TG_Modulation(u):
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
    coefficient = complex(math.sqrt(E/T))
    return [coefficient * cmath.exp(1j * math.pi * (phase[i] + 0.25)) for i in range(len(phase))]

def SOQPSK_TG_Demodulation(preamble, signal):

    samples_per_bit = SPS/2

    phase = (np.unwrap(np.angle(signal)) - 0.785416) / np.pi
    filtered = [0] + [phase[i+1] - phase[i] for i in range(1, len(phase)-1)] + [0]

    filter_offset = 0.015
    padded = [1 if filtered[i] > filter_offset else -1 if filtered[i] < -filter_offset else 0 for i in range(len(phase))]
    alpha = [padded[int(i * samples_per_bit)-1] for i in range(int(len(padded) / samples_per_bit))]

    bits = preamble[-2:]
    for i in range(2, len(alpha)):
        bits.append(int(((1 if (i%2 == 0) else -1) * (2*bits[i-1] - 1) * (1 - bits[i-2])) == alpha[i]))

    bits = bits[4:] + [0, 0, 0, 0]
    return bits


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


# Length of transmitted message
messageLength = 100

# Preamble (MUST be at least of length 2 for ternary demodulation)
preamble = [0,0,1,1,0,1,1,0,0,0,0,0,0,0]

# End value, ensures that entire message is modulated
end_message = [0,0,0,0,0,0,0]

#Generate message bits to be transmitted
message = np.random.randint(2, size=messageLength).tolist()

number_of_bits = len(preamble) + messageLength + len(end_message)
input_bits = preamble + message + end_message

# Modulate and demodulate signal
signal = SOQPSK_TG_Modulation(input_bits)
bits = SOQPSK_TG_Demodulation(preamble, signal)

print(number_of_bits, len(bits))

# Plot signal
plt.figure(figsize=(13, 7))
sub = plt.subplot(2,1,1)
plt.plot(range(len(signal)), np.real(signal))
plt.plot(range(len(signal)), np.imag(signal))
plt.title('SOQPSK TG signal')
plt.legend(['real', 'imaginary'], loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
plt.xlim((0,len(signal)+1))
plt.ylim(top=1.3)

sub = plt.subplot(2,1,2)
plt.plot(input_bits,'o')
plt.plot(bits, '*')
plt.title('Original vs Demodulated bits')
sub.legend(['Original', 'Demodulated'], loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
plt.xlim((-1,len(bits)))
plt.ylim(top=1.15)
plt.show()