#!/bin/bash

set -e

DEFAULT_PROBE_IDS=(1011217 1007159 1007645 1010332 13040 28430 51136 60323 62613 63017 63025 64237 1002750 1006295 1006896 1006948 17889 50941 14244 50524 1010769 1010672 1008228 1009988 1008786 1006477)
DEFAULT_TARGET=8.8.4.4

print_usage() {
    echo "Usage: $0 [OPTIONS] TARGET"
    echo "Options:"
    echo "  -p, --probes PROBE_ID...    Space-separated list of probe IDs (default: ${DEFAULT_PROBE_IDS[*]})"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Target: The target host for traceroute measurements (default: $DEFAULT_TARGET)"
    echo ""
    echo "This script performs traceroute measurements from passed RIPE probes to a target."
    echo ""
    echo "Example:"
    echo "  $0 --probes 1011217 google.com"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--probes)
            PROBE_IDS=()
            shift
            while [[ $# -gt 0 && ! "$1" =~ ^- && "$1" =~ ^[0-9]+$ ]]; do
                PROBE_IDS+=("$1")
                shift
            done
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            TARGET=$1
            shift
            ;;
    esac
done

PROBE_IDS=("${PROBE_IDS[@]:-${DEFAULT_PROBE_IDS[@]}}")
TARGET="${TARGET:-$DEFAULT_TARGET}"

echo "Using probes: [$(IFS=', '; echo "${PROBE_IDS[*]}")]"
echo "Target: $TARGET"

echo "Filtering for starlink probes..."

# For now, hardcode probe ASN ID 14593 worldwide or 45700 in Indonesia to identify Starlink probes based on ASN v4 ID
STARLINK_PROBES=()
for probe in "${PROBE_IDS[@]}"; do
    starlink_lines=$(ripe-atlas probe-info $probe | grep "ASN (IPv4)" | grep -e 14593 -e 45700 | wc -l)
    if [[ $starlink_lines -eq 0 ]]; then
        echo "Probe $probe is not a Starlink probe, skipping."
        continue
    fi

    STARLINK_PROBES+=("$probe")
done

echo "Performing measurement using probes [$(IFS=', '; echo "${STARLINK_PROBES[*]}")] to target $TARGET"
ripe-atlas measure traceroute --af 4 --interval 900 --from-probes "$(IFS=','; echo "${STARLINK_PROBES[*]}")" $TARGET
