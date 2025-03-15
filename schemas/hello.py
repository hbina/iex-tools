import argparse

from build.parsers import *
from utils import conditional


@conditional(numba.njit(cache=False))
def network_to_host_uint16(value: int) -> int:
    return ((value & 0xFF) << 8) | ((value >> 8) & 0xFF)


@conditional(numba.njit(cache=False))
def network_to_host_uint32(value: int) -> int:
    return (
            ((value & 0xFF) << 24) |
            (((value >> 8) & 0xFF) << 16) |
            (((value >> 16) & 0xFF) << 8) |
            ((value >> 24) & 0xFF)
    )


@conditional(numba.njit(cache=False))
def parse__len(buffer: np.ndarray, length: int):
    packet_buffer = buffer[:length]
    leftover_buffer = buffer[length:]

    return packet_buffer, leftover_buffer


@conditional(numba.njit(cache=False))
def parse_pcap(buffer: np.ndarray):
    # Parse Section Header Block
    if True:
        pcapng_header, buffer = parse__PcapngHeader(buffer)
        pcapng_section_header_block, buffer = parse__PcapngSectionHeaderBlock(buffer)

        # print("pcapng_header: ", pcapng_header)
        # print("pcapng_section_header_block: ", pcapng_section_header_block)
        block_len = pcapng_header[0]['PcapngHeader__block_total_length']

        assert pcapng_header[0]['PcapngHeader__block_type'] == 0x0a0d0d0a
        assert pcapng_section_header_block[0]['PcapngSectionHeaderBlock__byte_order_magic'] == 0x1a2b3c4d

        options_len = block_len - itemsize__PcapngHeader - itemsize__PcapngSectionHeaderBlock - 4
        assert options_len >= 0
        pcapng_options = np.frombuffer(buffer[:options_len], dtype=np.uint8)
        buffer = buffer[options_len:]
        pcapng_block_length_dup = np.frombuffer(buffer[:4], dtype=np.uint32)
        buffer = buffer[4:]

        assert pcapng_block_length_dup[0] == pcapng_header[0]["PcapngHeader__block_total_length"]

    # Parse Interface Description Block
    if True:
        pcapng_header, buffer = parse__PcapngHeader(buffer)
        pcapng_interface_description_block, buffer = parse__PcapngInterfaceDescriptionBlock(buffer)

        # print("pcapng_header:", pcapng_header)
        # print("pcapng_interface_description_block:", pcapng_interface_description_block)

        block_len = pcapng_header[0]['PcapngHeader__block_total_length']

        options_len = block_len - itemsize__PcapngHeader - itemsize__PcapngInterfaceDescriptionBlock - 4
        assert options_len >= 0
        pcapng_options = np.frombuffer(buffer[:options_len], dtype=np.uint8)
        buffer = buffer[options_len:]
        pcapng_block_length_dup = np.frombuffer(buffer[:4], dtype=np.uint32)
        buffer = buffer[4:]

        assert pcapng_block_length_dup[0] == pcapng_header[0]["PcapngHeader__block_total_length"]

    while True:
        # print("================")

        # Parse Enhanced Packet Block
        if True:
            pcapng_header, buffer = parse__PcapngHeader(buffer)
            pcapng_enhanced_packet_block, buffer = parse__PcapngEnhancedPacketBlock(buffer)

            block_len = pcapng_header[0]['PcapngHeader__block_total_length']
            captured_packet_len = pcapng_enhanced_packet_block[0]['PcapngEnhancedPacketBlock__captured_packet_length']
            original_packet_len = pcapng_enhanced_packet_block[0]['PcapngEnhancedPacketBlock__original_packet_length']

            assert captured_packet_len == original_packet_len

            packet_buffer, buffer = parse__len(buffer, captured_packet_len)

            options_len = block_len - itemsize__PcapngHeader - itemsize__PcapngEnhancedPacketBlock - captured_packet_len - 4
            assert options_len >= 0
            pcapng_options = np.frombuffer(buffer[:options_len], dtype=np.uint8)
            buffer = buffer[options_len:]
            pcapng_block_length_dup = np.frombuffer(buffer[:4], dtype=np.uint32)
            buffer = buffer[4:]

            assert pcapng_block_length_dup[0] == pcapng_header[0]["PcapngHeader__block_total_length"]

        ethernet_header, packet_buffer = parse__EthernetIIHeader(packet_buffer)
        ipv4_header, packet_buffer = parse__Ipv4Header(packet_buffer)
        udp_header, packet_buffer = parse__UdpHeader(packet_buffer)
        tp_header, packet_buffer = parse__TransportProtocolHeader(packet_buffer)

        # print("pcapng_header:", pcapng_header)
        # print("pcapng_enhanced_packet_block:", pcapng_enhanced_packet_block)
        # print("ethernet_header:", ethernet_header)
        # print("ipv4_header:", ipv4_header)
        # print("udp_header:", udp_header)
        # print("tp_header:", tp_header)

        source_port = network_to_host_uint16(udp_header['UdpHeader__source_port'])
        destination_port = network_to_host_uint16(udp_header['UdpHeader__destination_port'])

        # print(source_port, destination_port)
        # print("TransportProtocolHeader__send_time:", tp_header[0]["TransportProtocolHeader__send_time"])
        yield ethernet_header, ipv4_header, udp_header, tp_header, packet_buffer


@conditional(numba.njit(cache=False))
def numba_run(buffer):
    gen = parse_pcap(buffer)
    processed = 0
    for i in gen:
        ethernet_header, ipv4_header, udp_header, tp_header, packet_buffer = i
        processed += len(packet_buffer)
        if processed % 1_000_000 == 0:
            print(processed)
    print(processed)


parser = argparse.ArgumentParser()
parser.add_argument("path", type=str)
args = parser.parse_args()
mmap_buffer = np.memmap(args.path, dtype=np.uint8)
try:
    numba_run(mmap_buffer)
except StopIteration as e:
    pass
except Exception as e:
    raise e
