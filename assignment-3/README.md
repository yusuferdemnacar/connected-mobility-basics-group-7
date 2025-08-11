## Assignment 3
This assignment for Connected Mobility Basics has us evaluating bent-pipe latency for RIPE Atlas probes connected to Starlink.

### Install system dependencies
To run the measurement and reporting scripts `run.sh` and `report.sh`, the package `ripe-atlas` should be installed for CLI usage of the RIPE Atlas probes following the installation [guide](https://ripe-atlas-tools.readthedocs.io/en/latest/installation.html#installation). After you install the tool, you should authenticate to create measurements, but to get a report from an existing measurement, this should not be needed. To authenticate yourself with the CLI, follow the [example](https://ripe-atlas-tools.readthedocs.io/en/latest/use.html) on GitHub.

### Running
The `run.sh` script creates a periodic traceroute measurement to a given target, optionally taking in probe IDs. If no probe IDs are passed, default values are used, corresponding to about 20 probes belonging to group 7. The probe list is queried every 15 minutes, executing the traceroute command using IPv4 to the passed target.
We took the liberty of adding some random Starlink probes, because at the time of writing this, not all of the probes assigned to us were online and usable, or were not assigned to the Starlink AS (as identified by IPv4 ASN ID {14593|45700}). If no value is given for the TARGET option, the global Google DNS server `8.8.4.4` is used. For more information, refer to the usage advice of the script (run it with the `-h` flag).

### Reporting
The `report.sh` script creates a report from an existing measurement, optionally taking in start & stop times, and a filename. If no start time is supplied, the 1st of January 2025 is used, and similarly for end time, but in 2026.
For more information, refer to the usage advice of the script (run it with the `-h` flag).
This script creates a report from a given measurement, dumping all data matching its start and end time.

### Data parsing
The `parse.py` script calculates the bent pipe latency per probe and timestamp, and dumps it to a pickle file.
It takes as optional parameters the measurement output file, the traceroute target, and the gateway IP. For more information, refer to the usage advice of the script (run it with the `-h` flag: `$ python3 parse.py -h`).
This script parses the report file by iterating per probe and timestamp over the list of hops, and aggregating the hop latency until the gateway is reached. The median hop RTT is subtracted from the gateway median RTT hop, and two files are eventually created: one where all previous hops have been subtracted from the median gateway RTT, and one where those RTTs have not been subtracted. A gateway is reached if a hop with the GW IP address passed in is found; if the gateway decided to not report its IP address, the probe will not be evaluated. The script also reports statistics about the percentage of probes that reached their target, as well as the percentage of probes that contained the gateway.
A probe is considered to have reached its target if a hop was found matching the passed in target address.