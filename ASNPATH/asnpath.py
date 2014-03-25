#!/usr/bin/env python

import json
import urllib2
import sys
import PyASN
import mechanize

#targetAS=35228
targetAS=31655
transits=[6461,3356,174,3549,]
private=[1234,2345,3456,]

def lookupASN(p,ipaddr):

    return p.Lookup(ipaddr)          # should print 3356, the ASN for this IP

def loadASN():
    p = PyASN.new('ipasndat.gz')   # see below for more info
    print "[+] Total number of records loaded: %s" % p.records                    
    print ""
    return p

def checkAS(aspath):
    assize = len(aspath)
    ok = 0
    if aspath[ len(aspath) - 1 ] is not None:
        if aspath[ len(aspath) - 1 ] == targetAS:
            print "[+] Last AS: %s " % aspath[ len(aspath) - 2 ]
            checkas = aspath[ len(aspath) - 2 ]
        else:
            print "[+] Last AS: %s " % aspath[ len(aspath) - 1 ]
            checkas = aspath[ len(aspath) - 1 ]
    else:
        if aspath[ len(aspath) - 2 ] == targetAS:
            print "[+] Last AS: %s " % aspath[ len(aspath) - 3 ]
            checkas = aspath[ len(aspath) - 3 ]
        else:
            print "[+] Last AS: %s " % aspath[ len(aspath) - 2 ]
            checkas = aspath[ len(aspath) - 2 ]
    for i in range(len(transits)): 
         if transits[i] == checkas:
             print "[+] Transit Found"
             ok = 1
             continue

    if ok < 1:
        if assize ==  1:
            for i in range(len(transits)):
                if private[i] == checkas:
                    print "[+] Private Peer Found"
                    ok = True
                    continue
        else:
             print "[-] ALERT: Strange AS as last hop: %s " % checkas
             return(1)
    return(0)
    
#    elif ok :
#         print "[-] ALERT: Strange AS as last hop: %s " % checkas

     # else - Error

if __name__ == '__main__':

   if (sys.argv < 2):
      print "[-] Usage: %s <ripe url>" % sys.argv[0]
      exit(1)

   p = loadASN()
   data = json.load(urllib2.urlopen(sys.argv[1]))
   resp=0
  
   for probe in data:
        aspath=[]
        lastas=""
        probefrom = probe["from"]
        if probefrom:
            ASN = lookupASN(p,probefrom)
            print "[=] From: ",probefrom," ( AS",ASN,")"
#        print "[=] Source address: ",probe["src_addr"]
        print "[=] Probe ID: ",probe["prb_id"]
        result = probe["result"]
        for proberesult in result:
            ASN = {}
            if "result" in proberesult:
#                print "hop: ", proberesult["hop"],"  ",
                hopresult = proberesult["result"]
                rtt = []
                hopfrom = ""
                for hr in hopresult:
                    if "error" in hr:
                        rtt.append(hr["error"])
                    elif "x" in hr:
                        rtt.append(hr["x"])
                    else:
                        rtt.append(hr["rtt"])
#                        print hr["from"]
                        hopfrom = hr["from"]
                        ASN = lookupASN(p,hopfrom)
                if hopfrom:
#                    print "IP:", hopfrom," ASN: ", ASN, " "
                    if lastas != ASN:
                       aspath.append(ASN)
                       lastas=ASN
#                print rtt
            else:
                print "[-] Error: ",proberesult["error"]
#        print aspath
        
        resp += checkAS(aspath)

        print ""

   
   p = None                        
   exit(resp)
