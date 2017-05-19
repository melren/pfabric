#!/bin/bash

#clean up mininet
#mn -c

# Preliminary run command, need to loop this for each workload and control/scheduling type
python pfabric.py -t web -c tcp
