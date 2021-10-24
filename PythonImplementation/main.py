import modulation
import offset_correction
import demodulation
import numpy as np
from math import pi
from matplotlib import pyplot as plt


def plot_eye_diagram(signal, bits_per_symbol, n):
    fig = plt.figure()
    plt.subplot(2, 1, 1)
    plt.title('Eye Diagram for In-Phase Signal (I)')
    signal_graph = [num.real for num in signal]
    spacing = 2*bits_per_symbol
    for i in range(int(len(signal_graph)/spacing)-n):
        offset = i*spacing
        plt.plot(range(n), signal_graph[offset:offset+n])
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.xticks([0, int(n/2), n], ['-0.5', '0', '0.5'])

    plt.subplot(2, 1, 2)
    signal_graph = [num.imag for num in signal]
    for i in range(int(len(signal_graph)/spacing)-n):
        offset = i*spacing
        plt.plot(range(n), signal_graph[offset:offset+n])
    plt.title('Eye Diagram for Quadrature Signal (Q)')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.xticks([0, int(n/2), n], ['-0.5', '0', '0.5'])

    plt.show()


def plot_bit_comparison(tx_bits, rx_bits):
    plt.scatter(range(len(tx_bits)), tx_bits, edgecolors='blue')
    plt.scatter(range(len(rx_bits)), rx_bits, marker='*')
    plt.show()


if __name__ == '__main__':
    # Parameters specific to SOQPSK-TG
    T,  E, SPS = 1, 1, 20
    # offset values
    CFO, phaseOffset = 0.020, 0.035

    # create msg to transmit
    preamble = np.array([0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0])
    endMsg = np.array([0, 0, 0, 0, 0, 0, 0])
    data_len = 100
    data = np.random.randint(2, size=data_len)
    msg = np.concatenate([preamble, data, endMsg])
    msg_len = len(msg)

    # modulate msg
    signal = modulation.SOQPSK_TG_modulation(msg, T, E, SPS)

    # apply offset
    offset_signal = signal * np.exp(2j * pi * (CFO * np.arange(len(signal)) - phaseOffset))

    # send correction packet
    corr_pkt_len = 100
    corr_pkt = modulation.SOQPSK_TG_modulation(np.zeros(corr_pkt_len), T, E, SPS)
    corr_pkt *= np.exp(2j * pi * (CFO * np.arange(len(corr_pkt)) - phaseOffset))
    # use correction packet to get offsets
    cfo, po = offset_correction.calcOffsets(corr_pkt)
    # correct signal
    corr_signal = offset_correction.correctOffsets(offset_signal, cfo, po)

    # eye diagram
    plot_eye_diagram(corr_signal, int(SPS/2), 40)

    # demodulate
    bits = demodulation.SOQPSK_TG_Demod(preamble, signal, SPS)
    plot_bit_comparison(msg, bits)
