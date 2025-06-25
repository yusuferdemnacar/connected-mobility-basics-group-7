#!/bin/sh

# Usage: sudo ./channel-hopping.sh -i <interface>
if [ "$(id -u)" -ne 0 ]; then
	echo "This script must be run as root."
	exit 1
fi

set -e

DEFAULT_INTERFACE="wlan1"

while [[ $# -gt 0 ]]; do
	case $1 in
	-i | --interface)
		INTERFACE="$2"
		shift 2
		;;
	-h | --help)
		echo "Usage: sudo $0 [-i <interface>]"
		echo ""
		echo "Options:"
		echo "  -i, --interface   Interface to perform channel hopping on (default: 'wlan1')"
		echo "  -h, --help        Show this help message"
		exit 0
		;;
	*)
		echo "Unknown option: $1"
		echo "Usage: sudo $0 [-i <interface>]"
		exit 1
		;;
	esac
done

INTERFACE=${INTERFACE:-$DEFAULT_INTERFACE}

while true; do
	for channel in 1 2 3 4 5 6 7 8 9 10 11; do
		iwconfig $INTERFACE channel $channel
		echo "$INTERFACE now on channel $channel"
		sleep 2
	done
done
