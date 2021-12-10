from typing import List

import numpy as np
import math
from Packets_Py.MacPacket import MacPacket
from Packets_Py.MacPacket import PACKET_TYPE_MAP
import pyreedsolomon

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

    def make_bytearr_fec(self) -> bytearray:
        txbytes = bytearray()

        # This section defines the values to initialize the RS control
        # structure

        # T can be changed to increase or decrease error
        # correction capability
        T = 8 # number of errors that can be corrected

        sym_size = 8 # the size of the symbols, 8 bits or a byte

        # obtained from MATLAB using rsgenpoly(n,k) shouldn't be changed
        # unless the symbol size is changed
        gfpoly = 285

        total_len = 2**sym_size - 1 # n or the total length of the codeword

        # k or the length of the message to be encoded
        msg_len = total_len - 2*T
        fcr = 0 # first consecutive root
        prim = 1 # the primitve element to generate polynomial roots
        nroots = 2*T # the number of roots in the parity polynomial

        # initialize the Reed-Solomon control structure
        rs_dr = pyreedsolomon.Reed_Solomon(sym_size, msg_len, total_len, gfpoly, fcr, prim, nroots)

        for packet in self.__packets:
            bytearr = packet.get_bytes()

            # Perform Reed-Solomon encoding on bytearr chunk by chunk

            # find the number of whole chunks
            num_chunks = len(bytearr)//msg_len

            if num_chunks != 0:
                for i in range(num_chunks):
                    data_enc = rs_dr.encode(bytearr[i*msg_len:(i+1)*msg_len])
                    # add the encoded data to txbytes
                    txbytes.extend(data_enc)

            else:
                # if num_chunks is 0, range(num_chunks) returns none, which
                # causes error in the following when the conditional exectues
                i = 0

            # this checks if there's a partial chunk to be encoded
            if len(bytearr) != msg_len*num_chunks:
                to_pad = bytearray(bytearr[(i+1)*msg_len:])
                pad = bytearray(msg_len - len(to_pad))
                to_pad.extend(pad)
                # encode the padded chunk
                data_enc = rs_dr.encode(to_pad)
                # here the pad is removed and parity is added to txbytes
                txbytes.extend(data_enc[:len(bytearr[(i+1)*msg_len:])])
                txbytes.extend(data_enc[msg_len:])

        return txbytes
