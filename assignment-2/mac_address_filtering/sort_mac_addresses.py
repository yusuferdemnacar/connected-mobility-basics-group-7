from scapy.all import rdpcap, PPI_DOT11COMMON, Packet
from scapy.layers.dot11 import Dot11

mac_addresses_random = set()
mac_addresses_sorted = set()

def frequency_of_random_mac_addresses() -> float:
    return mac_addresses_random.__len__() / (mac_addresses_random.__len__() + mac_addresses_sorted.__len__())

def frequency_of_sorted_mac_addresses() -> float:
    return mac_addresses_sorted.__len__() / (mac_addresses_random.__len__() + mac_addresses_sorted.__len__())

def determent_if_mac_address_is_random(mac_address:str) -> bool:
    if mac_address is None or len(mac_address) != 17:
        return False
    first_octet = int(mac_address.split(":")[0], 16)
    is_random:bool = ((first_octet >> 1) & 0x01) == 0x01
    if is_random:
        mac_addresses_random.add(mac_address)
    else:
        mac_addresses_sorted.add(mac_address)
    return is_random
    
    
def processing_file(file_path: str):
    packets = rdpcap(file_path)
    for packet in packets:
        packet:Packet
        if packet.haslayer(Dot11):
            if packet.type == 0 and packet.subtype == 4:
                determent_if_mac_address_is_random(packet.addr2)

def main():
    file_path = "/Users/jonasjostan/Downloads/6.3.3.4.pcapng"
    processing_file(file_path)
    
    print(f"Frequency of random MAC addresses: {frequency_of_random_mac_addresses() * 100:.2f}%")
    print(f"Frequency of sorted MAC addresses: {frequency_of_sorted_mac_addresses() * 100:.2f}%")
    print(f"Total random MAC addresses: {len(mac_addresses_random)}")
    print(f"Total sorted MAC addresses: {len(mac_addresses_sorted)}")

if __name__ == "__main__":
    main()