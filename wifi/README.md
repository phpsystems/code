Wifi
====

Karmadetect.{sh,py}
-------------------

karmadetect is a few scripts to try to detect karma.

Current Status: possibly not working, needs more testing / clean up. 


wifihoneypot.sh
---------------

Script to set up your wifi interface in to monitor mode, then run airbase-ng 
to emulate Open, WEP, WPA and WPA2 networks.

To use:

run ./wifihoneyhot.sh &

When finished:

killall -9 airbase-ng


