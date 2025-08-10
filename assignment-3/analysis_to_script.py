import importlib
import parse
import matplotlib.pyplot as plt
import statistics
from argparse import ArgumentParser
from scipy.signal import savgol_filter
import datetime
from matplotlib.dates import DateFormatter, AutoDateLocator
import os

def process_measurement(output_filename: str, target_ip: str, gateway_ip: str):
    measurement_id = os.path.splitext(os.path.basename(output_filename))[0]
    os.makedirs(f"plots/{measurement_id}", exist_ok=True)
    measurements = parse.parse_measurements(output_filename, target_ip)

    # Measurement Counts
    # Total
    total_measurements = len(measurements)
    print(f"Total measurements: {total_measurements}")

    # By Probe ID
    measurements_by_probe_id = {}
    for measurement in measurements:
        if measurement.id not in measurements_by_probe_id:
            measurements_by_probe_id[measurement.id] = []
        measurements_by_probe_id[measurement.id].append(measurement)

    for probe_id, probe_measurements in measurements_by_probe_id.items():
        print(f"Probe ID: {probe_id},\tMeasurement count: {len(probe_measurements)}")

    # By Probe ID Plot
    probe_ids = list(measurements_by_probe_id.keys())
    measurement_counts = [len(measurements_by_probe_id[probe_id]) for probe_id in probe_ids]
    fig, ax = plt.subplots()
    ax.bar(probe_ids, measurement_counts)
    ax.set_xlabel('Probe ID')
    ax.set_ylabel('Measurement Count')
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_ha('right')
    fig.suptitle('Number of Measurements per Probe ID')
    fig.tight_layout()
    fig.savefig(f"plots/{measurement_id}/number_of_measurements_per_probe_id.png")
    plt.close(fig)

    # Successful vs Unsuccessful Measurements
    # Total
    total_measurements = len(measurements)
    print(f"Total measurements: {total_measurements}")
    successful_measurements = [m for m in measurements if m.reached_target]
    successful_count = len(successful_measurements)
    print(f"Successful measurements: {successful_count} ({successful_count / total_measurements * 100:.2f}%)")
    unsuccessful_measurements = [m for m in measurements if not m.reached_target]
    unsuccessful_count = len(unsuccessful_measurements)
    print(f"Unsuccessful measurements: {unsuccessful_count} ({unsuccessful_count / total_measurements * 100:.2f}%)")

    labels = ['Successful', 'Unsuccessful']
    sizes = [successful_count, unsuccessful_count]
    colors = ['#4CAF50', '#F44336']
    explode = (0.1, 0)
    fig, ax1 = plt.subplots()
    _ = ax1.pie(sizes, explode=explode, colors=colors, autopct='%.2f%%', startangle=135, pctdistance=1.2)
    _ = ax1.legend(labels, loc="upper right")
    _ = fig.suptitle('Ratio of Measurements Reaching Target (Successful) vs\nNot Reaching Target (Unsuccessful)')
    fig.savefig(f"plots/{measurement_id}/successful_vs_unsuccessful_ratio.png")
    plt.close(fig)

    # By Probe ID
    for probe_id, probe_measurements in measurements_by_probe_id.items():
        successful_count = sum(1 for m in probe_measurements if m.reached_target)
        unsuccessful_count = len(probe_measurements) - successful_count
        print(f"Probe ID: {probe_id},\tSuccessful: {successful_count},\tUnsuccessful: {unsuccessful_count}")

    # By Probe ID Plot
    fig, ax1 = plt.subplots()
    successful = [sum(1 for m in measurements_by_probe_id[probe_id] if m.reached_target) for probe_id in probe_ids]
    unsuccessful = [sum(1 for m in measurements_by_probe_id[probe_id] if not m.reached_target) for probe_id in probe_ids]
    ax1.bar(probe_ids, successful, label='Successful', color='#4CAF50')
    ax1.bar(probe_ids, unsuccessful, label='Unsuccessful', color='#F44336', bottom=successful)
    ax1.set_xlabel('Probe ID')
    ax1.set_ylabel('Measurement Count')
    ax1.set_ylim(0, max([s + u for s, u in zip(successful, unsuccessful)]) * 1.1)
    for label in ax1.get_xticklabels():
        label.set_rotation(45)
        label.set_ha('right')
    fig.suptitle('Successful vs Unsuccessful Measurements by Probe ID')
    _ = ax1.legend()
    fig.savefig(f"plots/{measurement_id}/successful_vs_unsuccessful_by_probe_id.png")
    plt.close(fig)

    # Gateway Visibility
    # Total
    gateway_present, gateway_absent = parse.get_probe_measurements_with_and_without_ip(measurements, gateway_ip)
    print(f"Measurements where gateway IP ({gateway_ip}) is present:\t{len(gateway_present)}")
    print(f"Measurements where gateway IP ({gateway_ip}) is absent:\t{len(gateway_absent)}")

    fig, ax1 = plt.subplots()
    labels = ['Gateway IP Present', 'Gateway IP Absent']
    sizes = [len(gateway_present), len(gateway_absent)]
    colors = ["#3595EE", "#FFB74D"]
    explode = (0.1, 0)
    _ = ax1.pie(sizes, explode=explode, colors=colors, autopct='%.2f%%', startangle=135, pctdistance=1.2)
    _ = ax1.legend(labels, loc="upper right", bbox_to_anchor=(1.35, 1))
    _ = fig.suptitle('Measurements with and without Gateway IP (' + gateway_ip + ')')
    fig.savefig(f"plots/{measurement_id}/gateway_visibility.png")
    plt.close(fig)

    # Total (with Success or Failure)
    gateway_present_successful = [m for m in gateway_present if m.reached_target]
    gateway_present_unsuccessful = [m for m in gateway_present if not m.reached_target]
    gateway_absent_successful = [m for m in gateway_absent if m.reached_target]
    gateway_absent_unsuccessful = [m for m in gateway_absent if not m.reached_target]
    print(f"Successful measurements where gateway IP ({gateway_ip}) is present: {len(gateway_present_successful)}")
    print(f"Successful measurements where gateway IP ({gateway_ip}) is absent: {len(gateway_absent_successful)}")
    print(f"Unsuccessful measurements where gateway IP ({gateway_ip}) is present: {len(gateway_present_unsuccessful)}")
    print(f"Unsuccessful measurements where gateway IP ({gateway_ip}) is absent: {len(gateway_absent_unsuccessful)}")
    fig, ax1 = plt.subplots(figsize=(6, 4.5))
    labels = ['Gateway IP Present - Successful', 'Gateway IP Present - Unsuccessful',
            'Gateway IP Absent - Successful', 'Gateway IP Absent - Unsuccessful']
    sizes = [len(gateway_present_successful), len(gateway_present_unsuccessful),
            len(gateway_absent_successful), len(gateway_absent_unsuccessful)]
    colors = ["#3595EE", "#90CAF9", "#FFB74D", "#FFE0B2"]
    explode = (0.1, 0, 0.1, 0)
    _ = ax1.pie(sizes, explode=explode, colors=colors, autopct='%.2f%%', startangle=135, pctdistance=1.2)
    _ = ax1.legend(labels, loc="upper right", bbox_to_anchor=(1.5, 1))
    _ = fig.suptitle('Measurements with and without Gateway IP (' + gateway_ip + ') present\nSubdivided by Success')
    _ = fig.tight_layout()
    fig.savefig(f"plots/{measurement_id}/gateway_visibility_by_success.png")
    plt.close(fig)

    # By Probe ID
    # We continue with only the successful measurements
    successful_measurements = []
    for probe_id, probe_measurements in measurements_by_probe_id.items():
        successful_measurements.extend([m for m in probe_measurements if m.reached_target])

    successful_measurements_by_probe_id = {}
    for measurement in successful_measurements:
        if measurement.id not in successful_measurements_by_probe_id:
            successful_measurements_by_probe_id[measurement.id] = []
        successful_measurements_by_probe_id[measurement.id].append(measurement)

    successful_measurements_gateway_presence_per_probe_id = {probe_id: {"present": [], "absent": []} for probe_id in measurements_by_probe_id.keys()}
    for probe_id, probe_measurements in successful_measurements_by_probe_id.items():
        present, absent = parse.get_probe_measurements_with_and_without_ip(probe_measurements, gateway_ip)
        successful_measurements_gateway_presence_per_probe_id[probe_id]["present"].extend(present)
        successful_measurements_gateway_presence_per_probe_id[probe_id]["absent"].extend(absent)

    print(f"Successful measurements with gateway IP ({gateway_ip}) presence by probe ID:")
    for probe_id in probe_ids:
        present_count = len(successful_measurements_gateway_presence_per_probe_id[probe_id]["present"])
        absent_count = len(successful_measurements_gateway_presence_per_probe_id[probe_id]["absent"])
        print(f"{'Probe ID:':<10} {probe_id:<10} {'Gateway IP Present:':<20} {present_count:<5} {'Gateway IP Absent:':<20} {absent_count:<5}")

    # By Probe ID Plot
    # Again, only successful measurements
    fig, ax1 = plt.subplots()
    successful_present = [len(successful_measurements_gateway_presence_per_probe_id[probe_id]["present"]) for probe_id in probe_ids]
    successful_absent = [len(successful_measurements_gateway_presence_per_probe_id[probe_id]["absent"]) for probe_id in probe_ids]
    ax1.bar(probe_ids, successful_present, label='Gateway IP Present', color='#3595EE')
    ax1.bar(probe_ids, successful_absent, label='Gateway IP Absent', color='#FFB74D', bottom=successful_present)
    ax1.set_xlabel('Probe ID')
    ax1.set_ylabel('Measurement Count')
    ax1.set_ylim(0, max([s + u for s, u in zip(successful_present, successful_absent)]) * 1.1)
    for label in ax1.get_xticklabels():
        label.set_rotation(45)
        label.set_ha('right')
    fig.suptitle('Successful Measurements by Probe ID\nSubdivided by Gateway IP Presence')
    _ = ax1.legend(loc="lower right")
    fig.savefig(f"plots/{measurement_id}/successful_measurements_by_probe_id_and_gateway_presence.png")
    plt.close(fig)

    # Bent Pipe Latency
    # For the probes that don't have the gateway IP 100.64.0.1 present in the trace, we assume the first visible IP is the gateway IP.
    # RTT Distribution per Probe ID
    data = []
    labels = []
    for probe_id in probe_ids:
        probe_latencies = []
        probe_measurements = successful_measurements_gateway_presence_per_probe_id[probe_id]["present"]
        for measurement in probe_measurements:
            for hop in measurement.hops:
                if hop.ip == gateway_ip and hop.rtt_times_ms:
                    mean_rtt = sum(hop.rtt_times_ms) / len(hop.rtt_times_ms)
                    probe_latencies.append(mean_rtt)

        if probe_latencies:
            data.append(probe_latencies)
            labels.append(str(probe_id))

            q1, q2, q3 = statistics.quantiles(probe_latencies, n=4)
            interquartile_range = q3 - q1
            lower_bound = q1 - 1.5 * interquartile_range
            upper_bound = q3 + 1.5 * interquartile_range

            outliers = [x for x in probe_latencies if x < lower_bound or x > upper_bound]
            inliers = [x for x in probe_latencies if lower_bound <= x <= upper_bound]

            print(f"Probe ID: {probe_id}")
            print(f"  Number of outliers: {len(outliers)}")
            print(f"  Number of inliers: {len(inliers)}")

    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    ax.boxplot(data, tick_labels=labels)
    ax.set_xlabel('Probe ID')
    ax.set_ylabel('RTT (ms)')
    ax.set_title('RTT Distribution for Successful Measurements with Gateway IP Present')
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_ha('right')
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    fig.tight_layout()
    fig.savefig(f"plots/{measurement_id}/rtt_distribution_successful_gateway_present.png")
    plt.close(fig)

    # Median RTT over Time per Probe ID
    probe_time_series = {probe_id: [] for probe_id in probe_ids}
    probe_time_stamps = {probe_id: [] for probe_id in probe_ids}
    for probe_id in probe_ids:
        probe_measurements = successful_measurements_gateway_presence_per_probe_id[probe_id]["present"]
        for measurement in sorted(probe_measurements, key=lambda m: m.timestamp):
            for hop in measurement.hops:
                if hop.ip == gateway_ip and hop.rtt_times_ms:
                    median_rtt = statistics.median(hop.rtt_times_ms)
                    probe_time_series[probe_id].append(median_rtt)
                    probe_time_stamps[probe_id].append(datetime.datetime.fromtimestamp(measurement.timestamp))
    fig, ax = plt.subplots(figsize=(20, 6))
    for probe_id in probe_ids:
        y = probe_time_series[probe_id]
        x = probe_time_stamps[probe_id]
        if len(y) >= 5:
            y_smooth = savgol_filter(y, window_length=13, polyorder=2)
            ax.plot(x, y_smooth, label=str(probe_id))
        else:
            ax.plot(x, y, label=str(probe_id))
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Median RTT (ms)")
    ax.set_title("Time Evolution of Median RTTs per Probe ID (Savitzky-Golay Smoothed)")
    ax.legend()
    ax.xaxis.set_major_locator(AutoDateLocator(minticks=10, maxticks=30))
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d\n%H:%M"))
    fig.autofmt_xdate()
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    fig.tight_layout()
    fig.savefig(f"plots/{measurement_id}/rtt_time_evolution_per_probe_id.png")
    plt.close(fig)

    # RTT Distribution per Continent per Probe ID
    continents = {
        "Africa": {},
        "Asia": {},
        "Europe": {},
        "North America": {},
        "Oceania": {},
        "South America": {}
    }

    for continent in continents:
        continents[continent] = {"probe_ids": []}

    continents["North America"]["probe_ids"].extend(["1011217", "1007159", "62613", "63017", "63025", "1006896", "1006948", ])
    continents["South America"]["probe_ids"].extend(["1007645"])
    continents["Europe"]["probe_ids"].extend(["1010332", "13040", "28430", "51136", "60323", ])
    continents["Oceania"]["probe_ids"].extend(["64237", "1008228"])
    continents["Africa"]["probe_ids"].extend(["1008786"])
    continents["Asia"]["probe_ids"].extend(["50524", "1010769", "1009988", "1006477"])

    for continent, info in continents.items():
        data = []
        labels = []
        for probe_id in info["probe_ids"]:
            probe_latencies = []
            probe_measurements = successful_measurements_gateway_presence_per_probe_id.get(probe_id, {}).get("present", [])
            for measurement in probe_measurements:
                for hop in measurement.hops:
                    if hop.ip == gateway_ip and hop.rtt_times_ms:
                        mean_rtt = sum(hop.rtt_times_ms) / len(hop.rtt_times_ms)
                        probe_latencies.append(mean_rtt)
            if probe_latencies:
                data.append(probe_latencies)
                labels.append(str(probe_id))
        if data:
            fig, ax1 = plt.subplots()
            ax1.boxplot(data, tick_labels=labels)
            ax1.set_xlabel('Probe ID')
            ax1.set_ylabel('RTT (ms)')
            ax1.set_title(f'RTT Distribution for {continent} (Gateway IP Present)')
            for label in ax1.get_xticklabels():
                label.set_rotation(45)
                label.set_ha('right')
            fig.tight_layout()
            fig.savefig(f"plots/{measurement_id}/rtt_distribution_{continent.lower().replace(' ', '_')}.png")
            plt.close(fig)

    for continent, info in continents.items():
        data = []
        labels = []
        for probe_id in info["probe_ids"]:
            probe_latencies = []
            probe_measurements = successful_measurements_gateway_presence_per_probe_id.get(probe_id, {}).get("present", [])
            for measurement in probe_measurements:
                for hop in measurement.hops:
                    if hop.ip == gateway_ip and hop.rtt_times_ms:
                        mean_rtt = sum(hop.rtt_times_ms) / len(hop.rtt_times_ms)
                        probe_latencies.append(mean_rtt)
            if probe_latencies:
                data.append(probe_latencies)
                labels.append(str(probe_id))
        if data:
            fig, ax1 = plt.subplots(figsize=(20, 10))
            for probe_id in info["probe_ids"]:
                y = probe_time_series.get(probe_id, [])
                x = probe_time_stamps.get(probe_id, [])
                if len(y) >= 5:
                    y_smooth = savgol_filter(y, window_length=13, polyorder=2)
                    ax1.plot(x, y_smooth, label=str(probe_id))
                elif len(y) > 0:
                    ax1.plot(x, y, label=str(probe_id))
            ax1.set_xlabel("Timestamp")
            ax1.set_ylabel("Median RTT (ms)")
            ax1.set_title(f"Time Evolution of Median RTTs per Probe ID in {continent} (Savitzky-Golay Smoothed)")
            ax1.legend()
            ax1.xaxis.set_major_locator(AutoDateLocator(minticks=10, maxticks=30))
            ax1.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d\n%H:%M"))
            fig.autofmt_xdate()
            ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
            fig.tight_layout()
            fig.savefig(f"plots/{measurement_id}/rtt_time_evolution_{continent.lower().replace(' ', '_')}.png")
            plt.close(fig)

def main():
    # Create a directory to save the plots
    if not os.path.exists("plots"):
        os.makedirs("plots")

    _ = importlib.reload(parse)

    DEFAULT_MEASUREMENT_FILENAME = ["measurements/measurements.txt"]
    DEFAULT_TARGET_IP = ["8.8.4.4"]
    DEFAULT_GATEWAY_IP = "100.64.0.1"
    parser = ArgumentParser(description="Parse reports created the parse script")
    parser.add_argument("--output", type=str, nargs='+', default=DEFAULT_MEASUREMENT_FILENAME, help=f"Output file names. Default is [{DEFAULT_MEASUREMENT_FILENAME}]")
    parser.add_argument("--target-ip", type=str, nargs='+', default=DEFAULT_TARGET_IP, help=f"Target IP address per measurement file. Default is [{DEFAULT_TARGET_IP}]")
    parser.add_argument("--gateway-ip", type=str, default=DEFAULT_GATEWAY_IP, help="Gateway IP address. Default is " + DEFAULT_GATEWAY_IP)

    args = parser.parse_args()
    measurements: list[str] = args.output
    target: list[str] = args.target_ip
    gateway_ip: str = args.gateway_ip

    for measurement, target_ip in zip(measurements, target):
        process_measurement(measurement, target_ip, gateway_ip)

if __name__ == "__main__":
    main()
