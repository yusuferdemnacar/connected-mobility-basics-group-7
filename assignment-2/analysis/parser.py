from scapy.all import rdpcap, Packet, PacketList
from scapy.layers.dot11 import Dot11
from pathlib import Path
from util import load_oui_dict

class PcapParser:
    RSSI = -70
    PACKET_TYPE = 0
    PACKET_SUBTYPE_BEACON = 4
    OUI_DICT = load_oui_dict(Path("oui.csv"))

    def __init__(self, pcap_file_path: Path):
        self.pcap_file_path: Path = pcap_file_path
        self.packets: PacketList = rdpcap(str(self.pcap_file_path))
        self.filtered_packets: PacketList = self.filter_packets(self.packets)

    def get_distribution_of_mac_addresses(self) -> tuple[int, int]:
        mac_addresses_random = set()
        mac_addresses_global = set()
        for packet in self.filtered_packets:
            is_random = is_random(packet.addr2)
            if is_random:
                mac_addresses_random.add(packet.addr2)
            else:
                mac_addresses_global.add(packet.addr2)
        return len(mac_addresses_random), len(mac_addresses_global)
    
    def filter_RSSI(self, packet:Packet) -> bool:
        return packet.dBm_AntSignal is not None and packet.dBm_AntSignal >= self.RSSI
    
    def filter_packet_type(self, packet:Packet) -> bool:
        return packet.type == self.PACKET_TYPE and packet.subtype == self.PACKET_SUBTYPE_BEACON
    
    def filter_packets(self, packets: PacketList) -> PacketList:
        packets = packets.filter(lambda p: p.haslayer(Dot11))
        packets = packets.filter(lambda p: self.filter_RSSI(p))
        packets = packets.filter(lambda p: self.filter_packet_type(p))
        return packets