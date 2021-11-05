# Plaground to use packets

import numpy as np
import zlib
import time
from MacPacket import MacHeader, MacPacket
from MacPacket import PACKET_TYPE_MAP
from PacketConstructor import DataPacketConstructor
from PacketReconstructor import PacketReconstructor


# Demonstration of creating 16-payload-bytes packets, creating a bytestream, and retrieving original data
# from said packet bytestream
if __name__ == '__main__':
    constructor = DataPacketConstructor('data.txt', 16)
    packets = constructor.make_packets()
    txbytes = constructor.make_bytearr()
    print(txbytes) #this bytestream will be sent over the communications channel

    packets_reconstructed = PacketReconstructor.reconstruct(txbytes)
    data_payload = PacketReconstructor.get_data_bytes(packets_reconstructed)
    print(data_payload)
