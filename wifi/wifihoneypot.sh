#!/bin/bash

SSID=$1
CHANNEL=$2
OPTS=$3

# setup up the monitoring interfaces
for i in `seq 0 1 4`; do
	airmon-ng start wlan0
done

# Open Authentication
airbase-ng -c $CHANNEL --essid "$SSID" -a aa:aa:aa:aa:aa:aa mon1 &
airbase-ng -c $CHANNEL --essid "$SSID" -a bb:bb:bb:bb:bb:bb mon2 -W 1 &
airbase-ng -c $CHANNEL --essid "$SSID" -a cc:cc:cc:cc:cc:cc mon3 -W 1 -z 2 &
airbase-ng -c $CHANNEL --essid "$SSID" -a dd:dd:dd:dd:dd:dd mon4 -W 1 -Z 4 &
 
wait

# Cleanup
for i in `seq 4 -1 0`; do
        airmon-ng stop mon$i
done
