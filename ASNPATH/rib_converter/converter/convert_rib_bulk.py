#!/usr/bin/python


# Bulk MRT RIB log conversion
# [to convert to a range of RIBs to IPASNDAT files]
# Author hadi asghari (hd dot asghari at gmail) of TUDelft.nl
# v1.0 on 01-dec-2009, v1.2 on 23-jan-2012 (added 32-bit asn support)


# file to use per day should be of these series:
# http://archive.routeviews.org/bgpdata/2009.11/RIBS/rib.20091125.0600.bz2


import bz2, time, sys,os, glob, datetime
import mrt_ex   # our own module

st = time.time()

print 'MRT RIB log importer v1.2'


# get range
if len(sys.argv) != 3:
    print 'Usage: convert_rib_bulk.py  START_DATE   END_DATE'
    print 'Dates should be in yyyy-mm-dd format.' 
    sys.exit()    

try:
    dt_rangestart = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    dt_rangeend   = datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d').date()
    print 'Starting bulk RIB conversion, from %s to %s...'  % (dt_rangestart, dt_rangeend)
    sys.stdout.flush()
except:
    print 'Malformed date. Try yyyy-mm-dd'
    sys.exit()

#
    
dt = dt_rangestart
dat__ = None


while dt <= dt_rangeend: 

    files = glob.glob('rib.%4d%02d%02d.????.bz2' % (dt.year, dt.month, dt.day))
    if not files:
        #print '%s no file!' % dt # debug
        dt += datetime.timedelta(days=1)            
        continue

    dump_file = files[0]
    f = bz2.BZ2File(dump_file, 'rb')    
    print "%s... " % dump_file[4:-4], 
    sys.stdout.flush()

    dat,skip,as32 = {},{},set()

    # get rib dump type
    s = f.read(mrt_ex.MRTHeader2.HDR_LEN)
    mrt_h = mrt_ex.MRTHeader2(s)
    tdv = 2 if mrt_h.type == mrt_ex.TABLE_DUMP_V2 else 1 if mrt_h.type == mrt_ex.TABLE_DUMP_V1 else -1
    if tdv == -1:
        raise Exception('unknown table_dump type')    

    f.seek(0)    
    nn = 0
    seq_no = -1
            
    while True:
        s = f.read(mrt_ex.MRTHeader2.HDR_LEN)
        if not s:
            break    
        assert len(s) == mrt_ex.MRTHeader2.HDR_LEN        
        mrt_h = mrt_ex.MRTHeader2(s)
        s = f.read(mrt_h.len)
        assert len(s) == mrt_h.len
         
                
        if tdv == 2:
            # TABLE_DUMP V2 importer                
            assert mrt_h.type == mrt_ex.TABLE_DUMP_V2        
            if mrt_h.subtype == mrt_ex.TableDumpV2.PEER_INDEX_TABLE:
                    continue 
            assert mrt_h.subtype == mrt_ex.TableDumpV2.RIB_IPV4_UNICAST

            td = mrt_ex.TableDumpV2(s)
            k = (td.cidr, td.bitmask)

            # no need for code to detect asn flips; as routeviews always takes the first match 
            owner = td.entries[0].as_path().owning_asn()                        
            assert owner is not None
        #
        
        elif tdv == 1:        
            # TABLE_DUMP-v1 importer code            
            assert mrt_h.type == mrt_ex.TABLE_DUMP_V1
            assert mrt_h.subtype == 1 # 'unexpected ip family: %d'

            td = mrt_ex.TableDumpV1(s)       
            k = (td.cidr, td.bitmask)        
            owner = None
            
            if (k not in skip) and (k not in as32) and (k not in dat):
                # only interested in getting the first match, that's why we check          
                owner = td.as_path().owning_asn()
                assert owner is not None
        #    


        if owner is not None:  
            if '{' in owner or '!' in owner: 
                skip[k]= owner
            else:              
                if '.' in owner: 
                    # convert 32 bit  asn format to non dot format
                    as32.add(owner)
                    owner = owner.split('.',1) 
                    owner = int(owner[0])*65536 + int(owner[1])
    	        dat[k]  = int(owner)
        #
        nn += 1            
        seq_no += 1
        if seq_no == 65536 and tdv == 1: 
            seq_no = 0
        assert td.seq == seq_no
    #

    f.close()

    try: del dat['0.0.0.0', 0]  # remove default route
    except: pass


    # CREATE OUTPUT FILE
    out_file  = 'ipasn_%d%02d%02d.dat' % (dt.year, dt.month, dt.day)    
    fw = open(out_file, 'w')    
    fw.write('; IP-ASN32-DAT file\n; Original file : %s\n' % dump_file)
    fw.write( '; Converted on  : %s\n; CIDRs         : %s\n; \n' % (time.asctime(), len(dat)) )

    for cidr_mask,asn in sorted(dat.iteritems()):
        s = '%s/%d\t%d\n' % (cidr_mask[0],cidr_mask[1],asn)
        fw.write(s)
    fw.close()    
    

    # compute difference
    changed = added = removed =  0
    if dat__ is not None:
        added = len( set(dat.keys()) - set(dat__.keys()) )
        removed = len( set(dat__.keys()) - set(dat.keys()) )
        for k, v in dat.iteritems():
            if dat__.get(k, v) != v: changed += 1
    #
    
    print '=> v%d recs:%d cidrs:%d 32b-asns:%d skipped:%d delta:(a%d d%d ch%d) @%.0fs'  % (tdv, nn, len(dat), len(as32),len(skip),added, removed, changed, time.time()-st)
    sys.stdout.flush()

    dat__ = dat
    dt += datetime.timedelta(days=1)
#


print 'Finished!'

