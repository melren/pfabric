#/usr/bin/python
# Implements traffic flow generation

import os
import random

def getFlowDist(traffic):
    
    flowSizes = []
    byteSizes = []
    random.seed(1111)
    
    if(traffic=="web"):
        # 95% of bytes come from 30% of flows 1-20MB
        # 5% of bytes come from 70% of flows <1 MB (assume minimum traffic size is 1MTU 1460bytes)
        for i in range(95):  
            byteSizes.append(random.randint(1024*1024, 20*1024*1024))
        for i in range(5):
            byteSizes.append(random.randint(1460, 1023*1024))

        # Populate flowSizes with 30 entries from values in byteSizes <=20MB & 70 entries from values < 1MB
        for i in range(30):
            flowSizes.append(random.choice(byteSizes[:95]))
        for i in range(70):
            flowSizes.append(random.choice(byteSizes[95:]))

    if(traffic=="data"):
        # >80% of bytes come from flows > 100MB, 80% of flows are < 10KB
        # Note we skip the byteSize step here because 20% from 10KB-100MB will not include 
        # enough values for use in the <10KB flows
        for i in range(19):
            # Define >100MB to be 101MB-500MB
            flowSizes.append(random.randint(101*1024*1024,500*1024*1024))
        for i in range(81):
            # Define <10KB to be 1MTU - 10KB
            flowSizes.append(random.randint(1460,10*1024))


    return flowSizes
