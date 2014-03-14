Wifi
====

Karmadetect.py
--------------

karmadetect.py is a script to try to detect karma.
The idea is, generate a random SSID, probe for it, and see if karma replies.

Current Status: possibly not working, needs more testing / clean up. 


wifihoneypot.sh
---------------

Script to set up your wifi interface in to monitor mode, then run airbase-ng 
to emulate Open, WEP, WPA and WPA2 networks.

To use:

run ./wifihoneyhot.sh &

When finished:

killall -9 airbase-ng


