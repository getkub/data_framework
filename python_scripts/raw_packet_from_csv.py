#! /usr/bin/env python
import sys
import os
import csv

# ========================================= #
# Wrapper python script to get payload from a CSV
# and trigger scapy with such a payload
# This has to be run as root user, as packet manipulation happens 
# Requires pypy 
# has to be run like   /some/directory/with/pypy <thisScript>
# ========================================= #
# Add Scapy module in path
baseDir=os.path.abspath('..')
scapyDir=baseDir + "/configs/binaries/scapy"
sys.path.append(scapyDir)
#print os.sys.path
from scapy.all import *

# This has to be run as root
if not os.geteuid() == 0:
    sys.exit("\nOnly root can run this script\n")


payloadCSV=baseDir + "/artefacts/rsyslog_mapped_data/scapy_mapping.csv"

# CSV format is: dst,src,sport,dport,payload
# Now pass these parameters to Scapy's core module
# Since it is localhost, L3socket needs to be used
conf.L3socket
conf.L3socket=L3RawSocket

with open(payloadCSV, mode='r') as payloadCSV_file:
    reader = csv.DictReader(payloadCSV_file)
    for row in reader:
        print(row['dst'], row['src'], row['sport'], row['dport'], row['payload'])
        packet = IP(dst=row['dst'],src=row['src'])/UDP(sport=int(row['sport']), dport=int(row['dport']))/Raw(load=row['payload'])
        send(packet)


