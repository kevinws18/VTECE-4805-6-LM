from typing import List

import math
from MacPacket import HEADER_BYTE_COUNT, MacPacket
from MacPacket import PACKET_TYPE_MAP
from MacPacket import SIZE_OFFSET

#Simple packet reconstructor
# TODO: must pull and verify in real time from a queue
class PacketReconstructor:
    def reconstruct(rxbytes:bytearray) -> List[MacPacket]:
        
        #First, generate a list of reconstructed packet objects
        packets = []

        while len(rxbytes) >= HEADER_BYTE_COUNT + 4:
            packet_size = int.from_bytes(rxbytes[SIZE_OFFSET:SIZE_OFFSET+2], 'big', signed=False)
            packet_bytes = rxbytes[0:packet_size]

            # TODO: implement FEC decoding on packet_bytes

            packets.append(MacPacket(packet_bytes))
            if not packets[-1].check_crc():
                return None # return None if the CRC is invalid
            rxbytes = rxbytes[packet_size:]
        
        packets.sort(key=lambda packet: packet.header().get_seq()) # sort the packets by sequence number
        return packets

    # retrieves the entire payload of a list of received packets
    def get_data_bytes(packets:List[MacPacket]) -> bytes:
        data_bytes = bytearray()
        for packet in packets:
            data_bytes += packet.get_data()

        return bytes(data_bytes)