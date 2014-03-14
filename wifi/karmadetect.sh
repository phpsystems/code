#!/bin/sh
INTERFACE=$1
SSID=$2
MAXCHANNELS=11
COUNT=0
DEBUG=1

iw dev $INTERFACE connect "$SSID"
# Start the Channel hopping
while test $COUNT -lt $MAXCHANNELS; do
	COUNT=`expr $COUNT + 1`
#	if test $DEBUG; then echo "Setting channel $COUNT"; fi
	# Change the Channel
#	iw dev $INTERFACE set channel $COUNT
	# Try to connect to a SSID
	iw dev $INTERFACE link
	if [ "$?" = 1 ]; then
		echo "SSID Connected"
	else
		echo "SSID Not Found"
	fi
	sleep 1
done

