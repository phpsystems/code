#! /usr/bin/env python
#
############################################
#                                          #
# Karma Detection - Alerts when people are #
# running "karma" nearby.                  #
#                                          #
# Copyright Tim Wilkes 2014                #
# All rights reserved.                     #
############################################

###########
# Imports #
###########

import os                           # For random SSID Generation
import sys                          # For the command line options
import signal                       # Signal Handling
import random
import string
import thread # 
from multiprocessing import Process


from scapy.all import *     # Packet library for generating probes.

###################
# Global Variable #
###################

SSID = ""       # SSID
sendInterfaces = ""

#############
# Functions #
#############

# Function to generate a random SSID
# This shouldn't exist, but will throw off
# Karma.
def randomSSID(size):
    return "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(size))

def setSSID():
    global SSID   
    SSID = randomSSID(8) # sufficiently long to prevent false positives.
 
# From http://wifimafia.blogspot.co.uk/2011/03/injecting-80211-frames-with-pylorcon2.html

# Function to send a Probe
# with the random SSID already 
# gernerated.
def sendProbe(sendInterface, probeFrequency=5):
    while (1):
        print "[+] Sending SSID Probe: %s on %s" % (SSID,sendInterface)
        # Send Probe
#       sendMac = get_if_hwaddr(sendInterface)
        probe = RadioTap()
        probe /= Dot11(type=0,subtype=4,addr1='ff:ff:ff:ff:ff:ff',addr2="00:c0:ca:6d:a2:02",addr3="ba:dc:fe:ab:cd:ef")
        probe /= Dot11ProbeReq()
        probe /= Dot11Elt(ID = 'SSID', info = SSID)
        probe /= Dot11Elt(ID = 'Rates',info="\x03\x12\x96\x18\x24\x30\x48\x60")
        probe /= Dot11Elt(ID = 'DSset',info='\x01')
        probe /= Dot11Elt(ID = 'TIM',info='\x00\x01\x00\x00')
  
        sendp(probe,iface=sendInterface, verbose=0)        
        
        time.sleep(probeFrequency)

# Function to check for the probe. 
# Only Karma should respond.
def checkProbeAck(p):
    if ( p.haslayer(Dot11ProbeResp) and p[Dot11Elt].info == SSID ) :
        mac=re.sub(':','',p.addr2)
        print "[+] Karma Detected : %s - %s " % (mac, p[Dot11Elt].info)
#    if ( p.haslayer(Dot11ProbeReq) and p[Dot11Elt].info == SSID ) :
#        mac=re.sub(':','',p.addr2)
#        print "[+] Probe Detected : %s - %s " % (mac, p[Dot11Elt].info)

#Channel Hopping.
def channel_hopper():
    while True:
        try:
            channel = random.randrange(1,15)
            os.system("iw dev %s set channel %d" % (sendInterfaces, channel))
            time.sleep(1)
        except KeyboardInterrupt:
            break


# The main function
def main(sendInterface, recieveInterface,debug=1):
    
    global sendInterfaces
    sendInterfaces=sendInterface
    print "[+] karmadetect.py by Tim Wilkes 2014 (c)"
    print "[+] Sending Interface : " + sendInterface
    print "[+] Monitoring on : " + recieveInterface
#    if sendInterface == recieveInterface:
#        print "[-] Can not send and recieve on the same interface"
#        sys.exit(1)
        
    # Generate random SSID
    setSSID()
    print "[+] SSID being used : " + SSID       

    p = Process(target = channel_hopper)
    p.start()    

    # Start the probing Thread:
    thread.start_new_thread(sendProbe, (sendInterface,5,))         
 
    # Now to check for a response.
    sniff(iface=recieveInterface,prn=checkProbeAck)

# Call the main Program
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage %s send_interface monitor_interface" % sys.argv[0]
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
    
