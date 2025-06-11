from itertools import takewhile
from pickle import dump
from argparse import ArgumentParser

# Disclaimer: Claude 4.0 helped writing this code, especially in plotting. Data processing and loading was done by us.

class Hop:
    def __init__(self, from_node: str, to_node: str, hop_time: float, from_node_degree: int) -> None:
        self.from_node = from_node
        self.to_node = to_node
        self.hop_time = hop_time  # Time it took for this specific hop
        self.from_node_degree = from_node_degree  # Node degree of the transmitting node at timestamp
    
    def __str__(self) -> str:
        return f"Hop({self.from_node} -> {self.to_node}, time: {self.hop_time:.3f}s, degree: {self.from_node_degree})"

class Message:
    """
    Message class to represent message data with the following attributes:
    - ID: Message identifier
    - distance: Distance travelled by the message
    - size: Size of the message in bytes
    - peer_density: Number of peer connections at message creation time
    - hop_count: Number of hops the message took
    - delivery_time: Time taken to deliver the message
    - is_delivered: Was the message delivered successfully
    - hops: the hops the message took (aggregated from transmissions and hops)
    """
    def __init__(self, message_id, distance=0, size=0, peer_density=0, hop_count=0, delivery_time=0, is_delivered=0):
        self.id = message_id
        self.distance = distance
        self.size = size
        self.peer_density = peer_density
        self.hop_count = hop_count
        self.delivery_time = delivery_time
        self.is_delivered = is_delivered
        self.hops: list[Hop] = []
        
    def setHops(self, hops: list[Hop]) -> None:
        self.hops = hops
    
    def __str__(self):
        return f"Message(id={self.id}, distance={self.distance}, size={self.size}, peer_density={self.peer_density}, hop_count={self.hop_count}, delivery_time={self.delivery_time}, is_delivered={self.is_delivered})"
        
class Transmission:
    """ Transmission represents a transmission of a message in hop
    - timestamp: timestamp when the transmission happened
    - from_node: the transmitting node
    - to_node: the node receiving the transmission
    - message_id: the ID of the message: this stays the same between hops
    - creation_time: time when the transmission was created
    - delivery_time: time when the transmission was delivered
    - total_delivery_time: total time it took for the transmission to be delivered, incl. hops
    """
    def __init__(self, timestamp: str, from_node: str, to_node: str, message_id: str, creation_time: str, delivery_time: str) -> None:
        self.timestamp = timestamp
        self.from_node = from_node
        self.to_node = to_node
        self.message_id = message_id
        self.hops: list[Hop] = []
        self.creation_time = creation_time
        self.delivery_time = delivery_time
        self.total_delivery_time=0.0 # TODO: check if there is a diff between delivery time and total delivery time
    
    def add_hop(self, hop: Hop) -> None:
        self.hops.append(hop)
        self.total_delivery_time += hop.hop_time

class TransmissionEvent:
    """ Transmission event represents more or less a message-related row in the event log report
    - timestamp: timestamp when the transmission happened
    - from_node: the transmitting node
    - to_node: the node receiving the transmission
    - message_id: the ID of the message: this stays the same between hops
    - action: C for created, S for sent, DE for delivery
    - extra: D for final delivery (transmission reached goal), or R for relayed (hop)
    """
    def __init__(self, timestamp: str, from_node: str, message_id: str, action: str, to_node = "", extra = "") -> None:
        self.timestamp = timestamp
        self.from_node = from_node
        self.message_id = message_id
        self.action = action
        self.to_node = to_node
        self.extra = extra
    def __str__(self) -> str:
        return f"TransmissionEvent({self.timestamp}: FROM {self.from_node} ID: {self.message_id} ACTION: {self.action}, TO_NODE: {self.to_node} EXTRA: {self.extra})"

def get_host_id_from_host_name(node_name: str) -> str:
    """
    Extract host ID from host name.
    Args:
        node_name: Host name in format 'lecturetaker_{groupid}_{hostid}' or 'selfstudier_{hostid}'
    Returns:
        Host ID as a string
    """
    is_lecture_taker = node_name.startswith('lecturetaker')
    splitted = node_name.split("_")
    return splitted[2] if is_lecture_taker else splitted[1]

def load_distance_delay_data(file_path) -> list[Message]:
    """
    Load distance delay report data
    Format: distance, delivery_time, hop_count, message_id
    """
    messages: list[Message] = []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                print(f"Skipped line: {line}")
                continue
            parts = line.split()
            if len(parts) >= 4:
                distance = float(parts[0])
                delivery_time = float(parts[1])
                hop_count = int(parts[2])
                message_id = parts[3]
                
                msg = Message(message_id, distance=distance, hop_count=hop_count, delivery_time=delivery_time, is_delivered=delivery_time == -1 or hop_count == -1)
                messages.append(msg)
            else:
                print("Cannot load distance delay delay of line due to missing 4 parts, have {} parts:", line, len(parts))
    return messages

def load_delivered_messages_data(file_path) -> dict[str, dict['size': int, 'hops': list[str]]]:
    """
    Load delivered messages report data
    Format: time, ID, size, hopcount, deliveryTime, fromHost, toHost, remainingTtl, isResponse, path
    
    Returns: Dict of message ID -> { size: message_size, hops: [node_ids]}
    """
    message_sizes_and_hops = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                print(f"Skipped line: {line}")
                continue
            parts = line.split()
            if len(parts) >= 3:
                message_id = parts[1]
                size = int(parts[2])
                hops = parts[-1].split('->')
                message_sizes_and_hops[message_id] = { 'size': size, 'hops': hops }
            else:
                print("Cannot load message delivery data line due to missing 3 parts, have {} parts:", line, len(parts))
    return message_sizes_and_hops

def parse_message_transmission_line(line: str) -> TransmissionEvent:
    """
    Parse a single line of message transmission data.
    
    Args:
        line: A string representing a line from EventLogReport.txt
        
    Returns:
        Transmission object with parsed data
    """
    parts = line.split()
    timestamp = float(parts[0])
    action = parts[1]
    from_node = parts[2]

    # Actions: 
    # C for created
    # S (Send) for message transfer started
    # DE for delivered
    # DR for dropped
    # A for delivered again
        
    # (self, timestamp: str, from_node: str, message_id: str, action: str, to_node = "", extra = "")
    if action == 'C':
        message_id = parts[3]
        return TransmissionEvent(timestamp, from_node, message_id, action)
    if (action == 'A') or (action == 'S') or (action == 'DE'):
        to_node = parts[3]
        if len(parts) < 5: 
            print("LINE CANNOT BE PARSED")
            print(line)
            return None
        else:
            message_id = parts[4]
            extra = parts[5] if action == 'DE' else '' # D for first delivery (message destination received the message/transmission), R for relayed
            return TransmissionEvent(timestamp, from_node, message_id, action, to_node, extra)
    else:
        return None # TODO: handle drop?

def parse_message_transmissions(event_log_file: str, message_ids_and_paths: dict[str, set[str]], connectivity_by_time: dict[float, dict[str, dict[str, set[str]]]]) -> dict[str, Transmission]:
    """
    Parse EventLogReport to extract message transmission events.
    
    Args:
        - event_log_file: Path to EventLogReport.txt
        - message_id_and_paths: message IDs, along with the path they took to their destination
        - connectivity_by_time: dictionary representing connectivity state at timestamp per node
        
    Returns:
        Dict of message ID to transmission with timing and hop information
    """
    transmissions = {}
    transmissions_events_per_message: dict[str, list[TransmissionEvent]] = {} # store all events per message ID

    with open(event_log_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or 'CONN' in line:
                # skip lines not related to messages, or comments
                continue
            transmission_event = parse_message_transmission_line(line)
            if transmission_event is None:
                continue

            # we only store transmission events that are part of the successful delivery of a message
            if transmission_event.message_id in message_ids_and_paths:
                path = message_ids_and_paths[transmission_event.message_id]
                if (transmission_event.from_node in path and transmission_event.action == 'C') or transmission_event.to_node in path: # either the created event, or for delivery the destination of this transmission is in the path
                    if transmission_event.message_id not in transmissions_events_per_message:
                        transmissions_events_per_message[transmission_event.message_id] = []
                    transmissions_events_per_message[transmission_event.message_id].append(transmission_event)
    
    for message_id, events in transmissions_events_per_message.items():
        path = message_ids_and_paths[message_id]

        # events are already sorted by timestamp
        created_event = next((t for t in events if t.action == 'C'), None) # only one created event per transmission
        if created_event is None:
            print(f"No created event found for message ID {message_id}. Skipping transmission. S")
            raise("fuck")
        
        delivered_event = next((t for t in events if t.extra == 'D'), None) # only one created event per transmission
        if delivered_event is None:
            print(f"No delivered event found for message ID {message_id}. Skipping transmission. Something is wrong")
            raise("fuck")
        hops = [created_event] + [t for t in events if t.action == 'DE' and t.extra == 'R'] + [delivered_event]
        
        hops_paired = list(zip(hops, hops[1:])) # Pair all delivered events with the created event and final delivery event to create hops
        
        transmission = Transmission(delivered_event.timestamp, created_event.from_node, delivered_event.to_node, created_event.message_id, created_event.timestamp, delivered_event.timestamp)
        
        for (from_hop, to_hop) in hops_paired:
            duration = float(to_hop.timestamp) - float(from_hop.timestamp)

            timestamp = from_hop.timestamp
            from_node = from_hop.from_node
            
            # Get neighbors for hop transmitting node at transmission time
            neighbors = get_neighbors_at_time_for_node(connectivity_by_time, timestamp, from_node)
            node_degree = len(neighbors)

            hop = Hop(from_hop.from_node, to_hop.to_node, duration, node_degree)
            transmission.add_hop(hop)

        transmissions[transmission.message_id] = transmission

    return transmissions

def parse_connectivity_report(connectivity_file: str) -> dict[float, dict[str, set[str]]]:
    """
    Parse ConnectivityONEReport to build a time-indexed connectivity graph.
    
    Args:
        connectivity_file: Path to ConnectivityONEReport.txt
        
    Returns:
        Dictionary mapping timestamp -> node -> set of connected nodes
    """
    connectivity_by_time: dict[float, dict[str, dict[str, set[str]]]] = {}
    
    with open(connectivity_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split()
            if len(parts) >= 5 and parts[1] == 'CONN':
                timestamp = float(parts[0])
                node1, node2 = parts[2], parts[3]
                status = parts[4]  # 'up' or 'down'
                
                if timestamp not in connectivity_by_time:
                    timestamp_connectivity_state = {}
                    timestamp_connectivity_state[node1] = {'up': set(), 'down': set()}
                    timestamp_connectivity_state[node2] = {'up': set(), 'down': set()}
                    connectivity_by_time[timestamp] = timestamp_connectivity_state
                if node1 not in connectivity_by_time[timestamp]:
                    connectivity_by_time[timestamp][node1] = {'up': set(), 'down': set()}
                if node2 not in connectivity_by_time[timestamp]:
                    connectivity_by_time[timestamp][node2] = {'up': set(), 'down': set()}

                connectivity_by_time[timestamp][node1][status].add(node2)
                connectivity_by_time[timestamp][node2][status].add(node1)
                    
    
    return connectivity_by_time

def get_neighbors_at_time_for_node(connectivity_state: dict[float, dict[str, dict[str, set[str]]]], 
                           target_time: float, node_name: str) -> set[str]:
    """
    Get the connectivity state at a specific time (or closest available time) for a specific node.
    
    Args:
        connectivity_state: Complete connectivity state by timestamp, node, and status
        target_time: The time to query
        node_name: Node name to built connectivity state for
        
    Returns:
        Connectivity state (node -> set of connected nodes)
    """
    # Find all timestamps <= target_time, take advantage of report being sorted
    valid_times = list(takewhile(lambda t: t <= target_time, connectivity_state.keys()))

    node_id = get_host_id_from_host_name(node_name)
    neighbors = set()
    for time in sorted(valid_times):
        connectivity_at_time = connectivity_state[time]
        if node_id in connectivity_at_time:
            # add all neighbours connected at the timestamp, and remove all neighbors that were dropped
            connections_established_at_time = connectivity_at_time[node_id]['up']
            neighbors |= connections_established_at_time
            
            connections_dropped_at_time = connectivity_at_time[node_id]['down']
            neighbors -= connections_dropped_at_time
    
    return neighbors

def load_transmission_data(event_log_file: str, connectivity_file: str, delivered_messages_with_hops: dict[str, set[str]]) -> dict[str, Transmission]:
    """
    Calculate peer density and latency for each transmitting node at the time of message transmission.
    
    Args:
        - event_log_file: Path to EventLogReport.txt
        - connectivity_file: Path to ConnectivityONEReport.txt
        - delivered_messages_with_hops: dictionary that maps delivered message ids to the paths they took
        
    Returns:
        Dict of message ID to transmission
    """
    print("Parsing connectivity report...")
    connectivity_by_time = parse_connectivity_report(connectivity_file)
    
    print("Parsing message transmissions...")
    transmissions = parse_message_transmissions(event_log_file, delivered_messages_with_hops, connectivity_by_time)
    
    print(f"Processed {len(transmissions)} transmission events.")
    
    return transmissions

def combine_message_data(scenario_prefix, size_suffixes, num_runs=100) -> list[Message]:
    """
    Combine data from different reports to create complete Message objects
    Supports aggregating data from multiple simulation runs
    """
    
    messages = []
    for size_suffix in size_suffixes:
        print(f"Combining messages of size {size_suffix}...")
        
        for run in range(1, num_runs + 1):
            distance_file = f"reports_data/{scenario_prefix}_{size_suffix}_run{run}_DistanceDelayReport.txt"
            delivered_file = f"reports_data/{scenario_prefix}_{size_suffix}_run{run}_DeliveredMessagesReport.txt"
            connectivity_file = f"reports_data/{scenario_prefix}_{size_suffix}_run{run}_ConnectivityONEReport.txt"
            eventlog_file = f"reports_data/{scenario_prefix}_{size_suffix}_run{run}_EventLogReport.txt"
            
            print(f"  Loading run {run}/{num_runs}...")
            # We load distance delay data for distance, delivery_time, hop_count, message_id        
            distance_messages = load_distance_delay_data(distance_file)
            # We load delivered message data for size and hop paths
            message_sizes_and_hops = load_delivered_messages_data(delivered_file)

            delivered_messages_with_hops = {}
            for message_id in message_sizes_and_hops.keys(): 
                delivered_messages_with_hops[message_id] = message_sizes_and_hops[message_id]['hops'] # TODO: need to map name to id?
            message_node_degrees = load_transmission_data(eventlog_file, connectivity_file, delivered_messages_with_hops)
            for msg in distance_messages:
                if msg.id in message_sizes_and_hops:
                    msg.size = message_sizes_and_hops[msg.id]['size']
                    msg.hops = message_node_degrees[msg.id].hops
                
                # Add run identifier to message id to avoid conflicts
                msg.id = f"{msg.id}_run{run}_{msg.size}"
                
                messages.append(msg)
                        
    return messages

def main():
    scenario_prefix = "CMB"
    
    DEFAULT_SIZE_SUFFIXES = ["100","1000","10000","100000","1000000","5000000"]
    DEFUALT_NUM_RUNS = 50

    parser = ArgumentParser(description="Combine reports generated from The ONE for assignment 1")
    parser.add_argument("--sizes", nargs="+", default=DEFAULT_SIZE_SUFFIXES, help="List of message sizes to process. Default is " + str(DEFAULT_SIZE_SUFFIXES))
    parser.add_argument("--runs", type=int, default=DEFUALT_NUM_RUNS, help="Number of runs to process for each size. Default is " + str(DEFUALT_NUM_RUNS))

    args = parser.parse_args()
    sizes = args.sizes
    runs = args.runs

    print(f"Received sizes {sizes}, and runs {runs}")

    print("Combining message data...")
    messages = combine_message_data(scenario_prefix, sizes, runs)
    print("Message data combined!")
    
    with open("message.pkl", "wb") as f:
        dump(messages, f)
if __name__ == "__main__":
    main()
