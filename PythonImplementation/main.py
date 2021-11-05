import soqpsk_tg
import numpy as np
from math import pi
from scipy import signal as filt
from matplotlib import pyplot as plt


def separate_baseband(signal):
    signal1 = signal * np.exp(2j * pi * -1/4 * np.arange(len(signal)))
    signal2 = signal * np.exp(2j * pi * 1/4 * np.arange(len(signal)))

    b, a = filt.butter(1, 0.5)

    signal1 = filt.filtfilt(b, a, signal1)
    signal2 = filt.filtfilt(b, a, signal2)

    return signal1, signal2


def plot_spectrum(signal, fs):
    fig = plt.figure()
    fft = np.fft.fftshift(np.fft.fft(signal))
    f = np.linspace(-fs/2, fs/2, len(fft))
    plt.plot(f, np.real(fft))
    plt.plot(f, np.imag(fft))
    plt.show()


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
    preamble = [0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0]
    end_msg = [0, 0, 0, 0, 0, 0, 0]
    data_len = 100
    data = np.random.randint(2, size=data_len).tolist()
    msg1 = preamble + data + end_msg
    data = np.random.randint(2, size=data_len).tolist()
    msg2 = preamble + data + end_msg
    msg_len = len(msg1)

    # modulate msg
    signal1 = soqpsk_tg.mod(msg1, T, E, SPS)
    signal1 *= np.exp(2j * pi * 1/4 * np.arange(len(signal1)))
    signal2 = soqpsk_tg.mod(msg2, T, E, SPS)
    signal2 *= np.exp(2j * pi * -1/4 * np.arange(len(signal2)))
    signal = signal1 + signal2

    # apply offset
    offset_signal = signal * np.exp(2j * pi * (CFO * np.arange(len(signal)) - phaseOffset))

    # send correction packet
    corr_pkt_len = 100
    corr_pkt = soqpsk_tg.mod(np.zeros(corr_pkt_len), T, E, SPS)
    corr_pkt *= np.exp(2j * pi * (CFO * np.arange(len(corr_pkt)) - phaseOffset))
    # use correction packet to get offsets
    cfo, po = soqpsk_tg.calcOffsets(corr_pkt)
    # correct signal
    corr_signal = soqpsk_tg.correctOffsets(offset_signal, cfo, po)

    output1, output2 = separate_baseband(corr_signal)

    # eye diagram
    #plot_eye_diagram(output1, int(SPS/2), 40)
    #plot_eye_diagram(output2, int(SPS/2), 40)

    # demodulate
    bits1 = soqpsk_tg.demod(preamble, output1, SPS)
    bits2 = soqpsk_tg.demod(preamble, output2, SPS)
    #bits = soqpsk_tg.demod(preamble, signal1, SPS)
    plot_bit_comparison(msg1, bits1)
    plot_bit_comparison(msg2, bits2)
    #plot_bit_comparison(msg1, bits)
