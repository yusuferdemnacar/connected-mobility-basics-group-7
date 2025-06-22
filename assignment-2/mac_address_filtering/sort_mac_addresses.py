from scapy.all import rdpcap, PPI_DOT11COMMON, Packet, PacketList
from scapy.layers.dot11 import Dot11

class packet_parser:
    mac_addresses_random = set()
    mac_addresses_sorted = set()
    RSSI = -70
    PACKET_TYPE = 0
    PACKET_SUBTYPE_BEACON = 4

    def frequency_of_random_mac_addresses(self) -> float:
        sum_of_mac_addresses = self.calculate_sum_of_mac_addresses()
        if sum_of_mac_addresses == 0:
            return 0.0
        return self.mac_addresses_random.__len__() / sum_of_mac_addresses

    def calculate_sum_of_mac_addresses(self) -> int:
        return self.mac_addresses_random.__len__() + self.mac_addresses_sorted.__len__()
    
    def frequency_of_sorted_mac_addresses(self) -> float:
        sum_of_all_mac_addresses = self.calculate_sum_of_mac_addresses() 
        if sum_of_all_mac_addresses == 0:        
            return 0.0
        return self.mac_addresses_sorted.__len__() / sum_of_all_mac_addresses
    def determent_if_mac_address_is_random(self, mac_address:str) -> bool:
        if mac_address is None or len(mac_address) != 17:
            return False
        first_octet = int(mac_address.split(":")[0], 16)
        is_random:bool = ((first_octet >> 1) & 0x01) == 0x01
        if is_random:
            self.mac_addresses_random.add(mac_address)
        else:
            self.mac_addresses_sorted.add(mac_address)
        return is_random
    
    def filter_RSSI(self, packet:Packet) -> bool:
        return packet.dBm_AntSignal is not None and packet.dBm_AntSignal >= self.RSSI
    
    def filter_packet_type(self, packet:Packet) -> bool:
        return packet.type == self.PACKET_TYPE and packet.subtype == self.PACKET_SUBTYPE_BEACON
        
                    
        
    
    def processing_file(self, file_path: str):
        packets:PacketList = rdpcap(file_path)
        packetList = packets.filter(lambda p: p.haslayer(Dot11))
        packetList = packetList.filter(lambda p: self.filter_RSSI(p))
        packetList = packetList.filter(lambda p:self.filter_packet_type(p))
        for packet in packetList:
            self.determent_if_mac_address_is_random(packet.addr2)
            
            

def main():
    file_path = ""
    parser = packet_parser()
    parser.processing_file(file_path)
    
    print(f"Frequency of random MAC addresses: {parser.frequency_of_random_mac_addresses() * 100:.2f}%")
    print(f"Frequency of sorted MAC addresses: {parser.frequency_of_sorted_mac_addresses() * 100:.2f}%")
    print(f"Total random MAC addresses: {len(parser.mac_addresses_random)}")
    print(f"Total sorted MAC addresses: {len(parser.mac_addresses_sorted)}")

if __name__ == "__main__":
    main()