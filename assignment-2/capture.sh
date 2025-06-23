#!/bin/bash 

# This script requires sudo
# Usage: sudo ./capture.sh -i <interface> [ -f <filter> ] -o <output_file>
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root."
    exit 1
fi

set -e

DEFAULT_OUTPUT_FILE="capture.pcap"
DEFAULT_FILTER="wlan[0] == 0x40" # Capture wifi probe requests

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--interface)
            INTERFACE="$2"
            shift 2
            ;;
        -f|--filter)
            FILTER="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

OUTPUT_FILE=${OUTPUT_FILE:-$DEFAULT_OUTPUT_FILE}
FILTER=${FILTER:-$DEFAULT_FILTER}

if [ -z "$INTERFACE" ]; then
    echo "Please specify the network monitor to sniff on using -i or --interface followed by the interface name, as specified on ip l"
    exit 1
fi

# Bring down network interface to set it to monitor mode
ifconfig $INTERFACE down
iwconfig $INTERFACE mode Monitor
ifconfig $INTERFACE up

# Make sure file exists and is writeable
touch $OUTPUT_FILE
chmod 666 $OUTPUT_FILE

echo "Capturing packets on interface $INTERFACE with filter '$FILTER' to file '$OUTPUT_FILE' - press Ctrl+C to stop capturing"

tshark -i $INTERFACE -f "$FILTER" -w $OUTPUT_FILE
