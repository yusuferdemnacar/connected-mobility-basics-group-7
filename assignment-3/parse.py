import datetime
from argparse import ArgumentParser
from statistics import median
from typing import Any, Dict, Optional, Tuple
from pickle import dump

class Hop:
    def __init__(self, ip: str, rtt_times_ms: list[float]) -> None:
        self.id = id
        self.ip = ip
        self.rtt_times_ms = rtt_times_ms

        # extension for the geolocation
        self.geolocation: Optional[Dict[str, Any]] = None

    def add_geolocation(self, geolocation_data: Dict[str, Any]) -> None:
        self.geolocation = geolocation_data

    def get_geolocation(self) -> Optional[Dict[str, Any]]:
        return self.geolocation

class ProbeMeasurement:
    def __init__(self, id: str, timestamp: int, hops: list[Hop], reached_target: bool) -> None:
        self.id = id
        self.timestamp = timestamp
        self.hops = hops
        self.reached_target = reached_target

def parse_measurements(filename: str, target: str) -> list[ProbeMeasurement]:
    with open(filename, "r") as f:
        data = f.readlines()

    probe_measurements: list[ProbeMeasurement] = []

    data_length = len(data)
    i=0
    while i < data_length:
        line = data[i]
        is_probe_line = line.startswith("Probe #")
        if not is_probe_line:
            i += 1
            continue 
        probe_id = line.split("#")[1].strip()
        hop_lines: list[str] = []
        timestamp_str = data[i+1].strip()
        timestamp_str = " ".join([part for part in timestamp_str.split() if part != "CEST"])
        timestamp = datetime.datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %Y")
        timestamp = int(timestamp.timestamp())
        j = i + 2 # next line is the date, the one after that is empty
        target_found = False
        maximum_ttl_reached = False
        while not maximum_ttl_reached and not target_found and j < len(data):
            next_line = data[j].strip()
            if not next_line:
                j += 1
                continue
            if next_line.startswith("Probe #"):
                break
            hop_lines.append(next_line)
            if target in next_line:
                target_found = True

            # There can be a case where the target is reached, but the server does not respond to traceroutes (replies with * instead of IP)
            # Check if hop index is 255
            hop_index = next_line.split()[0]
            if hop_index == "255":
                maximum_ttl_reached = True
            j += 1

        hops: list[Hop] = []
        for line in hop_lines:
            # 2 172.16.251.4                            33.987 ms    21.974 ms    36.805 ms
            # 1 *                                               *            *            *
            # 2 172.16.251.4                            26.515 ms    21.743 ms            *

            # Skip lines that are not valid hop lines (e.g., error messages)
            if not line.strip() or not line.strip()[0].isdigit():
                continue

            parts = line.split()
            if len(parts) < 5:
                continue
            hop_ip = parts[1]
            rtt_times: list[float] = []

            parts = parts[2:]  # remove the IP
            ms_indices = [idx for idx, part in enumerate(parts) if part == "ms"] # to get lists of equal length, join cells that start with 'ms' with the cell before them
            star_indices = [idx for idx, part in enumerate(parts) if part == "*"]
            rtt_cells = sorted([parts[idx - 1] for idx in ms_indices] + [parts[idx] for idx in star_indices]) # get * values

            for rtt_time in rtt_cells:
                if rtt_time != "*":
                    rtt_times.append(float(rtt_time))
            hops.append(Hop(ip=hop_ip, rtt_times_ms=rtt_times))
        is_successful = any(hop.ip == target for hop in hops)
        probe = ProbeMeasurement(id=probe_id, timestamp=timestamp, hops=hops, reached_target=is_successful)
        probe_measurements.append(probe)
        i = j # jump all the hops belonging to this probe
    
    return probe_measurements

def get_probe_measurements_with_and_without_ip(probe_measurements: list[ProbeMeasurement], ip: str) -> Tuple[list[ProbeMeasurement], list[ProbeMeasurement]]:
    """
    Filters the probe measurements to include those that have a hop with the specified IP and those that do not.
    Returns a tuple of two lists: (with_ip, without_ip).
    """
    with_ip: list[ProbeMeasurement] = []
    without_ip: list[ProbeMeasurement] = []
    for probe in probe_measurements:
        if any(hop.ip == ip for hop in probe.hops):
            with_ip.append(probe)
        else:
            without_ip.append(probe)
    return with_ip, without_ip

def get_bent_pipe_per_probe(probe_measurements: list[ProbeMeasurement], gateway_ip: str, exclude_before: bool) -> Dict[Tuple[str, int], float]:
    """
    Calculates the bent pipe for each probe measurement, which is the time until the gateway hop
    If exclude_before is True, it excludes hops before the gateway hop.
    returns a dictionary, indexed by a tuple composed of the probeid and timestamp, which returns the bent pipe latency for that timestamp until the gateway hop.
    """
    bent_pipe_per_probe: Dict[Tuple[str, int], float] = {}
    for probe in probe_measurements:
        gateway_in_probe = next(filter(lambda hop: hop.ip == gateway_ip, probe.hops), None) is not None
        if not gateway_in_probe:
            continue

        total_before_gateway = 0.0
        for hop in probe.hops:
            if hop.ip != gateway_ip:
                total_before_gateway += median(hop.rtt_times_ms)
            else:
                gateway_rtt =  median(hop.rtt_times_ms) - (total_before_gateway if exclude_before else 0)
                bent_pipe_per_probe[(probe.id, probe.timestamp)] = gateway_rtt
                break
        

    return bent_pipe_per_probe
    
def main():
    DEFAULT_OUTPUT_FILENAME="output.txt"
    DEFAULT_TARGET="8.8.4.4"
    DEFAULT_GATEWAY_IP="100.64.0.1"

    parser = ArgumentParser(description="Parse report created by ripe-atlas")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_FILENAME, help="Output file name. Default is " + DEFAULT_OUTPUT_FILENAME)
    parser.add_argument("--target", type=str, default=DEFAULT_TARGET, help="Traceroute target IP address. Default is " + DEFAULT_TARGET)
    parser.add_argument("--gateway-ip", type=str, default=DEFAULT_GATEWAY_IP, help="Traceroute gateway IP address. Default is " + DEFAULT_GATEWAY_IP)
    args = parser.parse_args()
    output_filename: str = args.output
    target: str = args.target
    gateway_ip: str = args.gateway_ip

    print(f"Using target {target}")
    print(f"Using output file name {output_filename}")
    print(f"Using gateway IP {gateway_ip}")

    probe_measurements = parse_measurements(output_filename, target)
    print(f"Parsed {len(probe_measurements)} probe measurements")
    
    measurements_with_gw = get_probe_measurements_with_and_without_ip(probe_measurements, gateway_ip)[0]
    successful_measurements = [probe for probe in probe_measurements if probe.reached_target]
    length_with_gateway = len(measurements_with_gw)
    p_gw: float = (length_with_gateway / len(probe_measurements)) * 100
    p_successful: float = (len(successful_measurements) / len(probe_measurements)) * 100
    print(f"Found {len(measurements_with_gw)}: {p_gw:.2f}% probe measurements with gateway hop {gateway_ip}. ")
    print(f"Found {len(successful_measurements)}: {p_successful:.2f}% successful probe measurements. ")

    # TODO: look into measurements whose first hop with a meaningful (e.g. more than 10ms) RTT and is not 100.64.0.1: is it only that the GW did not resolve, or is it potentially other GWs?
    bent_pipe_per_probe_without = get_bent_pipe_per_probe(probe_measurements, gateway_ip, False)
    bent_pipe_per_probe = get_bent_pipe_per_probe(probe_measurements, gateway_ip, True)

    with open("without.pkl", "wb") as f:
            dump(bent_pipe_per_probe_without, f)
    with open("with.pkl", "wb") as f:
            dump(bent_pipe_per_probe, f)

    # probe_id = "1006896"
    # timestamp_str = "Fri Jul 18 18:22:26 CEST 2025"
    # timestamp_str = " ".join([part for part in timestamp_str.split() if part != "CEST"])
    # timestamp = datetime.datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %Y")
    # timestamp = int(timestamp.timestamp())

    # without = bent_pipe_per_probe_without[(probe_id, timestamp)]
    # inc = bent_pipe_per_probe[(probe_id, timestamp)]

    # print(f"Bent pipe excluding hops before gateway hop: {without}ms")
    # print(f"Bent pipe including hops before gateway hop: {inc}ms")

if __name__ == "__main__":
    main()
