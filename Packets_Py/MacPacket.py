# MacPacket.py

# This object represents a single packet in the MAC layer.
# A header, data payload, and a trailer is included
import zlib
from Packets_Py.BitMasks import *
import numpy as np

HEADER_BYTE_COUNT = 7
TRAILER_BYTE_COUNT = 4
FRAME_CONTROL_OFFSET = 0
SRC_ADDR_OFFSET = 1
DST_ADDR_OFFSET = 2
SEQ_NUM_OFFSET = 3
SIZE_OFFSET = 5
PACKET_TYPE_MAP = {'DATA': 0, 'ACK': 1, 'RTS': 2, 'CTS': 3}

PREAMBLE = 0b00110100.to_bytes(1, 'big')


class MacHeader:
    def __init__(self, bytearr: bytearray=None):
        if bytearr is None:
            self.__bytes = bytearray(HEADER_BYTE_COUNT)
        else:
            self.__bytes = bytearr

    def set_src(self, addr: bytes) -> None:
        self.__bytes[SRC_ADDR_OFFSET] = addr

    def get_src(self) -> bytes:
        return self.__bytes[SRC_ADDR_OFFSET]

    def set_dst(self, addr: bytes) -> None:
        self.__bytes[DST_ADDR_OFFSET] = addr

    def get_dst(self) -> bytes:
        return self.__bytes[DST_ADDR_OFFSET]

    def set_type(self, type: bytes) -> None:
        self.__bytes[FRAME_CONTROL_OFFSET] &= ~TYPE_BITMASK # reset type bits
        self.__bytes[FRAME_CONTROL_OFFSET] |= (type << TYPE_SHIFT) # set type bits
        
    def get_type(self) -> bytes:
        return (self.__bytes[FRAME_CONTROL_OFFSET] & TYPE_BITMASK) >> TYPE_SHIFT

    def set_seq(self, seq: np.uint16) -> None:
        self.__bytes[SEQ_NUM_OFFSET] = (seq & (0xff << 8)) >> 8
        self.__bytes[SEQ_NUM_OFFSET + 1] = seq & 0xff

    def get_seq(self) -> np.uint16:
        return int.from_bytes(self.__bytes[SEQ_NUM_OFFSET:SEQ_NUM_OFFSET+2], 'big', signed=False)

    def set_size(self, size: np.uint16) -> None:
        self.__bytes[SIZE_OFFSET] = (size & (0xff << 8)) >> 8
        self.__bytes[SIZE_OFFSET + 1] = size & 0xff

    def get_size(self) -> np.uint16:
        return int.from_bytes(self.__bytes[SIZE_OFFSET:SIZE_OFFSET+2], 'big', signed=False)

    def get_bytes(self) -> bytearray:
        return self.__bytes


class MacPacket:
    def __init__(self, rxbytes: bytearray = None):
        if rxbytes is not None:
            self.reconstruct_packet(rxbytes)

    def reconstruct_packet(self, rxbytes: bytearray):
        self.__header = MacHeader(rxbytes[0:HEADER_BYTE_COUNT])
        self.__data = bytes(rxbytes[HEADER_BYTE_COUNT:-4]) # all except final 4 bytes is data payload
        self.__crc = int.from_bytes(rxbytes[-4:], 'big', signed=False) #CRC is final 4 bytes
        self.__retryCount = None # received packets to not keep track of retries

    def init_new_packet(self, src: bytes, dst: bytes, seq: np.uint16, type: bytes, data:bytes = None) -> None:
        self.__data = data
        self.__header = MacHeader()
        self.__init_header(src, dst, seq, type)
        self.__retryCount = 0
        self.__crc = self.__calc_crc()

    def __init_header(self, src: bytes, dst: bytes, seq: np.uint16, type: bytes) -> None:
        self.__header.set_type(type)
        self.__header.set_src(src)
        self.__header.set_dst(dst)
        self.__header.set_seq(seq)
        packet_size = HEADER_BYTE_COUNT + len(self.__data) + 4 # CRC 32 will always be 4 bytes
        self.__header.set_size(packet_size)

    def __calc_crc(self):
        if self.__data is not None:
            arr = self.__header.get_bytes() + bytearray(self.__data)
        else:
            arr = self.__header.get_bytes()
        return zlib.crc32(arr)

    def check_crc(self) -> bool:
        actual_crc = self.__calc_crc()
        return actual_crc == self.__crc

    def get_crc(self):
        return self.__crc

    def header(self):
        return self.__header

    def get_data(self) -> bytes:
        return self.__data

    def increment_retry(self):
        self.__retryCount += 1

    def get_retries(self):
        return self.__retryCount

    def get_bytes(self) -> bytearray:
        crc_bytes = self.__crc.to_bytes(4, 'big')
        return PREAMBLE + self.__header.get_bytes() + bytearray(self.__data) + bytearray(crc_bytes)

