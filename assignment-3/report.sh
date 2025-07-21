#!/bin/sh

DEFAULT_START_TIME="2025-01-01T00:00:00Z"
DEFAULT_END_TIME="2026-01-01T00:00:00Z"
DEFAULT_FILENAME="output.txt"

print_usage() {
    echo "Usage: $0 [OPTIONS] MEASUREMENT_ID"
    echo "Options:"
    echo "  -s, --start-time start time of the measurements. ISO 8601 formatted date-time in UTC. (default: ${DEFAULT_START_TIME})"
    echo "  -e, --end-time end time of the measurements. ISO 8601 formatted date-time in UTC. (default: ${DEFAULT_END_TIME})"
    echo "  -f, --filename Specify the output filename. (default: ${DEFAULT_FILENAME})"
    echo "  -h, --help Show this help message."
    echo "MEASUREMENT_ID: The ID of the measurement to report on."
    echo "Example: $0 118424999 --start-time 2025-01-01T00:00:00Z --end-time 2026-01-02T00:00:00Z"
}

while [ $# -gt 0 ]; do
    case "$1" in
        -s|--start-time)
            START_TIME="$2"
            shift 2
            ;;
        -e|--end-time)
            END_TIME="$2"
            shift 2
            ;;
        -f|--filename)
            FILENAME="$2"
            shift 2
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            MEASUREMENT_ID="$1"
            shift
            ;;
    esac
done

if [ -z "$MEASUREMENT_ID" ]; then
    echo "Error: MEASUREMENT_ID is required."
    print_usage
    exit 1
fi

START_TIME=${START_TIME:-$DEFAULT_START_TIME}
END_TIME=${END_TIME:-$DEFAULT_END_TIME}
FILENAME=${FILENAME:-$DEFAULT_FILENAME}

echo "Using start time: $START_TIME"
echo "Using end time: $END_TIME"
echo "Output will be saved to: $FILENAME"
echo "Generating report for measurement ID: $MEASUREMENT_ID"

ripe-atlas report --start-time "$START_TIME" --stop-time "$END_TIME" "$MEASUREMENT_ID" > "$FILENAME"