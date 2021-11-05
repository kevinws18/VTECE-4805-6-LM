from typing import List

import numpy as np
import math
from MacPacket import MacPacket
from MacPacket import PACKET_TYPE_MAP

class DataPacketConstructor:
    def __init__(self, filename:str, data_mtu: int = 1024):
        f = open(filename, 'rb')
        self.data = f.read()
        self.__mtu = data_mtu

    def make_packets(self) -> List[MacPacket]:
        num_packets = len(self.data) // self.__mtu + 1
        packet_size = math.ceil(len(self.data) / num_packets)

        packets = []
        for packet_num in range(num_packets):
            packets.append(MacPacket())
            start_byte = packet_num * packet_size
            end_byte = start_byte + packet_size
            packets[packet_num].init_new_packet(1, 2, packet_num, PACKET_TYPE_MAP['DATA'], data=self.data[start_byte:end_byte])
        
        self.__packets = packets
        return packets

    def make_bytearr(self) -> bytearray:
        txbytes = bytearray()
        for packet in self.__packets:
            bytearr = packet.get_bytes()

            # TODO: perform FEC encoding on bytearr
            
            txbytes += bytearr

        return txbytes