import numpy as np

def SOQPSK_TG_Demodulation(preamble, signal):
    SPS=20
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

def SOQPSK_TG_Demod(preamble, signal, SPS):
    samples_per_bit = SPS/2

    phase = (np.unwrap(np.angle(signal)) - 0.785416) / np.pi

    filtered = np.zeros(len(phase))
    for x in range(1, len(phase)-1):
        filtered[x] = phase[x+1] - phase[x]

    filter_offset = 0.015
    padded = np.zeros(len(phase))
    for i in range(len(padded)):
        if filtered[i] > filter_offset:
            padded[i] = 1
        elif filtered[i] < -filter_offset:
            padded[i] = -1

    alpha = np.zeros(int(len(padded)/samples_per_bit))
    for x in range(1, len(alpha)):
        alpha[x-1] = padded[(int((x-1) * samples_per_bit))]

    starter = [preamble[-2], preamble[-1]]
    bits = np.zeros(len(alpha))
    bits[0] = starter[0]
    bits[1] = starter[1]
    for x in range(2, len(alpha)):
        if ((1 if (x % 2 == 0) else -1) * (2 * bits[x - 1] - 1) * (1 - bits[x-2])) == alpha[x]:
            bits[x] = 1

    bits = bits[4:]
    bits = np.append(bits, [0, 0, 0, 0])
    return bits
