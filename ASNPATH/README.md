ASNPATH
=======

Scripts to take the download reports from RIPE's atlas project (https://atlas.ripe.net/about/) in JSON format,
then look at the traceroutes to find out which AS they belong to.

This can then be used to alert if the penultimate hop is not on a list of approved AS Numbers to provide routing. 
If the number of ASs is less than 2, ingnore the alert, as that is private peering.





Rib_converter
-------------

NOT My Work.

rib_converter was downloaded from:

http://pyasn.googlecode.com/files/rib_converter.zip


RIBs
----

RIB downloaded from:

http://archive.routeviews.org/bgpdata/2014.03/RIBS/

To update the list, from rib_converter dir, run:

python ./converter/convert_rib.py ./rib.20140325.1200.bz2 ../ipasndat.gz


PyASN
-----

PyASN Downloaded from:

http://pyasn.googlecode.com/files/PyASN-1.2.zip

To Install run:

./code/ASNPATH/PyASN/PyASN-1.2# python ./setup.py install


From RIPE Atlas
---------------

Code help:

https://atlas.ripe.net/docs/code/

How to convert the json file to a traceroute.

https://atlas.ripe.net/dstatic/measurements/python/json2traceroute.py
