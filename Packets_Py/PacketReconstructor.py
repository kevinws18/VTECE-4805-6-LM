from typing import List

import math
import pyreedsolomon
from Packets_Py.MacPacket import HEADER_BYTE_COUNT, MacPacket
from Packets_Py.MacPacket import PACKET_TYPE_MAP
from Packets_Py.MacPacket import SIZE_OFFSET

#Simple packet reconstructor
# TODO: must pull and verify in real time from a queue
class PacketReconstructor:
    def reconstruct(rxbytes:bytearray) -> List[MacPacket]:

        #First, generate a list of reconstructed packet objects
        packets = []

        # This section defines the values that initialize the RS control
        # structure

        # T can be changed to increase or decrease error
        # correction capability
        T = 8 # number of errors that can be corrected

        # obtained from MATLAB using rsgenpoly(n,k) shouldn't be changed
        # unless the symbol size is changed
        gfpoly = 285

        sym_size = 8 # the size of the symbols, bytes
        total_len = 2**sym_size - 1 # n or the total length of the codeword

        # k or the length of the message to be encoded
        msg_len = total_len - 2*T
        fcr = 0 # first consecutive root
        prim = 1 # the primitve element to generate polynomial roots
        nroots = 2*T # the number of roots in the parity polynomial

        # initialize the Reed-Solomon control structure
        rs_dr = pyreedsolomon.Reed_Solomon(sym_size, msg_len, total_len, gfpoly, fcr, prim, nroots)

        #while len(rxbytes) >= HEADER_BYTE_COUNT + 4:

        packet_size = int.from_bytes(rxbytes[SIZE_OFFSET:SIZE_OFFSET+2], 'big', signed=False)
        #packet_bytes = rxbytes[0:packet_size]

        packet_bytes = bytearray()

        # Perform Reed-Solomon decoding on rxbytes

        # the number of bytes corresponding to a packet after adding parity
        # is: packet_size + ceil(packet_size/msg_len)*nroots
        pkt_len = packet_size + math.ceil(packet_size/msg_len)*nroots

        num_pkts = len(rxbytes)// pkt_len

        for i in range(num_pkts):
            packet_bytes = bytearray()

            # copy the chunk
            pkt_chunk = rxbytes[i*pkt_len:(i+1)*pkt_len]

            # figure out how many complete chunks were in the packet
            num_chunks = len(pkt_chunk)//total_len

            # start chunking up the data corresponding to each packet
            # and decode
            for n in range(num_chunks):
                # decode the chunk
                data_dec, n_errors = rs_dr.decode(pkt_chunk[n*total_len:(n+1)*total_len])

                # add the decoded bytes to packet_bytes
                packet_bytes.extend(data_dec)

            # this checks if theres a partial chunk to be decoded
            if len(pkt_chunk) != total_len*num_chunks:
                #take the payload portion and trailer and store in to_pad
                to_pad = pkt_chunk[(n+1)*total_len: len(pkt_chunk)-nroots]

                #create the pad
                pad = bytearray(total_len - len(to_pad) - nroots)
                #add the pad
                to_pad.extend(pad)
                #add the parity to the end
                to_pad.extend(pkt_chunk[len(pkt_chunk)-nroots:])

                #decode
                data_dec, n_errors = rs_dr.decode(to_pad)

                #add the result of decoding without padding
                packet_bytes.extend(data_dec[:msg_len-len(pad)])

            #form the packet and append to packets
            packets.append(MacPacket(packet_bytes))

            if not packets[-1].check_crc():
                return None # return None if the CRC is invalid
            #rxbytes = rxbytes[packet_size:]

        packets.sort(key=lambda packet: packet.header().get_seq()) # sort the packets by sequence number
        return packets

    # retrieves the entire payload of a list of received packets
    def get_data_bytes(packets:List[MacPacket]) -> bytes:
        data_bytes = bytearray()
        for packet in packets:
            data_bytes += packet.get_data()

        return bytes(data_bytes)
