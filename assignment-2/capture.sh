#!/bin/sh

# Usage: sudo ./capture.sh -m <probe|network> [-o <output_file>] [-i <interface>] [-f <capture filter>]
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root."
    exit 1
fi

set -e

DEFAULT_OUTPUT_FILE="capture.pcap"
DEFAULT_FILTER="wlan[0]==0x40" # wifi probe requests
DEFAULT_INTERFACE="wlan1"

while [[ $# -gt 0 ]]; do
    case $1 in
    -m | --mode)
        MODE="$2"
        shift 2
        ;;
    -o | --output)
        OUTPUT_FILE="$2"
        shift 2
        ;;
    -i | --interface)
        INTERFACE="$2"
        shift 2
        ;;
    -f | --filter)
        FILTER="$2"
        shift 2
        ;;
    -h | --help)
        echo "Usage: sudo $0 -m <probe|network> [-o <output_file>] [-i <interface>] [-f <capture filter>]"
        echo ""
        echo "Modes:"
        echo "  probe   - Capture all WiFi probe requests"
        echo "  network - Capture all incoming traffic on the network interface"
        echo ""
        echo "Options:"
        echo "  -m, --mode        Capture mode: 'probe' or 'network'"
        echo "  -f, --filter      tshark filter (default: 'wlan[0]==0x40')"
        echo "  -i, --interface   Interface to capture requests on (default: 'wlan1')"
        echo "  -o, --output      Output file (default: 'capture.pcap')"
        echo "  -h, --help        Show this help message"
        exit 0
        ;;
    *)
        echo "Unknown option: $1"
        echo "Usage: sudo $0 -m <probe|network> [-o <output_file>] [-i <interface>] [-f <capture filter>]"
        exit 1
        ;;
    esac
done

OUTPUT_FILE=${OUTPUT_FILE:-$DEFAULT_OUTPUT_FILE}
INTERFACE=${INTERFACE:-$DEFAULT_INTERFACE}
FILTER=${FILTER:-$DEFAULT_FILTER}

if [ -z "$MODE" ]; then
    echo "Error: Mode is required (-m option)"
    echo "Available modes: 'probe' (capture probe requests) or 'network' (capture all traffic)"
    exit 1
fi

capture_probe_requests() {
    echo "Setting interface to monitor mode for probe request capture"

    ifconfig $INTERFACE down
    iwconfig $INTERFACE mode Monitor
    ifconfig $INTERFACE up
    echo "Set $INTERFACE to monitor mode"

    capture_network_traffic $FILTER

}

capture_network_traffic() {
    local filter=$1
    echo "Capturing traffic on interface $INTERFACE"
    echo "Capturing to file '$OUTPUT_FILE'"
    echo "With capture filter '$filter'"
    echo "Press Ctrl+C to stop capturing"

    tshark -i $INTERFACE -f "$filter" -w $OUTPUT_FILE
}

# Main logic based on mode
case "$MODE" in
"probe" | "network")
    # Make sure output file is writeable
    touch $OUTPUT_FILE
    chmod o=rw $OUTPUT_FILE
    case "$MODE" in
    "probe")
        capture_probe_requests $FILTER
        ;;
    "network")
        capture_network_traffic ''
        ;;
    esac
    ;;
*)
    echo "Error: Invalid mode '$MODE'"
    echo "Available modes: 'probe' or 'network'"
    exit 1
    ;;
esac
