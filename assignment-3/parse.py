import datetime
import time
from math import inf
from argparse import ArgumentParser
from statistics import median

class Hop:
    def __init__(self, ip: str, rtt_times_ms: list[float]) -> None:
        self.id = id
        self.ip = ip
        self.rtt_times_ms = rtt_times_ms

class ProbeMeasurement:
    def __init__(self, id: str, timestamp: int, hops: list[Hop], reached_target: bool) -> None:
        self.id = id
        self.timestamp = timestamp
        self.hops = hops
        self.reached_target = reached_target

def parse_output(filename: str, target: str) -> list[ProbeMeasurement]:
    with open(filename, "r") as f:
        data = f.readlines()

    probe_measurements: list[ProbeMeasurement] = []

    data_length = len(data)
    i=0
    fail_count=0
    while i < data_length:
        line = data[i]
        length_probes = len(probe_measurements)
        is_probe_line = line.startswith("Probe #")
        if not is_probe_line:
            i += 1
            continue 
        probe_id = line.split("#")[1].strip()
        hop_lines = []
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

        hops = []
        for line in hop_lines:
            # 2 172.16.251.4                            33.987 ms    21.974 ms    36.805 ms
            # 1 *                                               *            *            *
            # 2 172.16.251.4                            26.515 ms    21.743 ms            *

            parts = line.split()
            if len(parts) < 5:
                raise ValueError(f"Line '{line}' does not have all necessary components to be a hop line: {parts}")
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
        is_successfull = target_found or not maximum_ttl_reached # TODO: verify assumption that a successful probe is one that either reaches the target or does not reach the maximum TTL
        if not is_successfull:
            fail_count += 1
        probe = ProbeMeasurement(id=probe_id, timestamp=timestamp, hops=hops, reached_target=is_successfull)
        probe_measurements.append(probe)
        i = j # jump all the hops belonging to this probe

    print(f"Failed to reach target {target} in {fail_count} probes out of {len(probe_measurements)} total probes.")
    return probe_measurements

def get_probe_measurements_with_gateway_hop(probe_measurements: list[ProbeMeasurement], gateway_ip: str) -> list[ProbeMeasurement]:
    """
    Filters the probe measurements to only include those that have a hop with the specified gateway IP.
    """
    filtered_measurements: list[ProbeMeasurement] = []
    for probe in probe_measurements:
        for hop in probe.hops:
            if hop.ip == gateway_ip:
                filtered_measurements.append(probe)
                break
    return filtered_measurements

def get_bent_pipe_per_probe(probe_measurements: list[ProbeMeasurement], gateway_ip: str, exclude_before: bool) -> list[dict[(str, int), float]:]:
    """
    Calculates the bent pipe for each probe measurement, which is the time until the gateway hop
    If exclude_before is True, it excludes hops before the gateway hop.
    """
    bent_pipe_per_probe = []
    # WIP
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

    probe_measurements = parse_output(output_filename, target)
    print(f"Parsed {len(probe_measurements)} probe measurements")
    
    measurements_with_gw = get_probe_measurements_with_gateway_hop(probe_measurements, gateway_ip)
    successful_measurements = [probe for probe in probe_measurements if probe.reached_target]
    length_with_gateway = len(measurements_with_gw)
    p_gw: float = (length_with_gateway / len(probe_measurements)) * 100
    p_successful: float = (len(successful_measurements) / len(probe_measurements)) * 100
    print(f"Found {len(measurements_with_gw)}: {p_gw:.2f}% probe measurements with gateway hop {gateway_ip}. ")
    print(f"Found {len(successful_measurements)}: {p_successful:.2f}% successful probe measurements. ")

    # TODO: look into measurements whose first hop with a meaningful (e.g. more than 10ms) RTT and is not 100.64.0.1: is it only that the GW did not resolve, or is it potentially other GWs?
    bent_pipe_per_probe = get_bent_pipe_per_probe(probe_measurements, gateway_ip, False)
    bent_pipe_per_probe = get_bent_pipe_per_probe(probe_measurements, gateway_ip, True)
if __name__ == "__main__":
    main()
