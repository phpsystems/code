#!/usr/bin/python

# MRT RIB log import  [to convert to a text IP-ASN lookup table]
# Author hadi asghari (hd dot asghari at gmail) of TUDelft.nl
# v1.0 on 25-nov-2009, v1.1 on 02-dec-2009
# v1.2 on 23-jan-2012 - add 32bit asn support


# file to use per day should be of these series:
# http://archive.routeviews.org/bgpdata/2009.11/RIBS/rib.20091125.0600.bz2


import bz2, time, sys
import mrt_ex   # our own module, also included

print 'MRT RIB log importer v1.2'

if len(sys.argv) != 3:
    print '\nUsage:  convert_rib.py   <ribmrtdump_file.bz2>   <ipasndat_file.gz>'
    print '\nDownload RIBs from: http://archive.routeviews.org/bgpdata/2009.xx/RIBS/xxx.bz2'		
    sys.exit()


dump_file = sys.argv[1] 
out_file  = sys.argv[2] 
st = time.time()


f = bz2.BZ2File(dump_file, 'rb')

dat,skip,as32 = {},{},set()


# get rib dump type
s = f.read(mrt_ex.MRTHeader2.HDR_LEN)
mrt_h = mrt_ex.MRTHeader2(s)
tdv = 2 if mrt_h.type == mrt_ex.TABLE_DUMP_V2 else 1 if mrt_h.type == mrt_ex.TABLE_DUMP_V1 else -1
if tdv == -1:
    raise Exception('unknown table_dump type')

print 'Processing %s\nRIB TableDumpV%d' % (f.name, tdv)
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
        if nn % 5000 == 1: 
            print '.',
            sys.stdout.flush()
            
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
        if nn % 100000 == 1: 
            print '.',
            sys.stdout.flush()
        
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
        if '{' in owner or '!' in owner:  # curly & exception. '!' is in v1 files.
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

print '\nRecords processed: %d in %.1fs' % (nn, time.time()-st)


# WRITE OUTPUT FILE
fw = open(out_file, 'w') 

fw.write('; IP-ASN32-DAT file\n; Original file : %s\n' % dump_file)
fw.write('; Converted on  : %s\n; CIDRs         : %s\n; \n' % (time.asctime(), len(dat)) )

for cidr_mask,asn in sorted(dat.iteritems()):
    s = '%s/%d\t%d\n' % (cidr_mask[0],cidr_mask[1],asn)
    fw.write(s)
fw.close()


print 'IPASNDAT file saved (%d CIDRs, %d 32b-asns, skipped:%d)' % (len(dat), len(as32), len(skip))

