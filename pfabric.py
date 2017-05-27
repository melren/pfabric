#!/usr/bin/python

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from argparse import ArgumentParser
from time import sleep, time
from fattopo import FatTree, OVSBridgeSTP
from startopo import StarTopo
#from workloads import *
from flows import flow

import os
import random
#import numpy as np

parser = ArgumentParser(description="Runs pFabric Implementation")
parser.add_argument('--out', '-o',
            help="Directory to store outputs",
            default="outputs/")
parser.add_argument('--traffic', '-t',
            help="Type of traffic, use: 'web' or 'data'",
            required=True)
parser.add_argument('--cong','-c',
            help="Type of congestion control, use: 'tcp', 'mintcp', or 'none'(udp)",
            required=True)
parser.add_argument('--kary', '-k',
            help="Size of K for fat tree topology, default = 3",
            type=int,
                    default=3)
parser.add_argument('--hosts', '-n',
            help="Number of hosts to use for star topology, default = 54",
                    type=int,
            default=54)
parser.add_argument('--topo',
                    help="Type of topology to use for network: 'star' or 'fattree', default = star",
            default="star")

args = parser.parse_args()

if args.cong not in ['tcp', 'mintcp', 'none']:
    parser.error('Wrong congestion method, use: tcp, mintcp, or none')
if args.traffic not in ['web','data']:
    parser.error('Wrong traffic type, use: web or data')
if args.kary < 1 or args.kary > 3:
    parser.error('Value of k must be between 1 and 3')
if args.hosts < 1:
    parser.error('Number of hosts must be at least 1')
if args.topo not in ['star','fattree']:
    parser.error('Wrong network topology, use: star or fattree')

def adjustSysSettings(cong, topo):
    if(cong!="none"):
        print "Changing TCP and buffer queue size settings..."
        os.system("sudo ./congestion/%s.sh" % cong)
        qSize = 1000
        if(cong=="mintcp"):
            # MTU = 1460 bytes, pFabric qSize = 36864 bytes ~ 36KB
            qSize = (36000/1460)
        if(cong=="tcp"):
            # TCP-DropTail qSize = 230400 bytes ~ 225KB
            qSize = (225000/1460)

        if(topo=="star"):
            size = args.hosts

            for n in range(1,size+1):
                os.system("sudo ifconfig s0-eth%d txqueuelen %d" % (n,qSize))
        else:
            # size = (args.kary/2)**2 * args.kary
            csNum = (args.kary/2)**2
            asNum = ((args.kary/2)*args.kary)
            # esNum = asNum
        
            for i in range(0,csNum):
                for j in range(0,args.kary):
                    os.system("sudo ifconfig cs_%d-eth%d txqueuelen %d" % (i, j, qSize+1))
            for i in range(0,asNum):
                for j in range(0,args.kary):
                    os.system("sudo ifconfig as_%d_0-eth%d txqueuelen %d" % (i, j, qSize+1))
                    os.system("sudo ifconfig es_%d_0-eth%d txqueuelen %d" % (i, j, qSize+1))

def resetSystem():
    print "Restoring pre-run system settings..."
    os.system("sudo ./congestion/tcp.sh")

def addPriorityQDisc(switch):
    for intf in switch.intfList():
        if (str(intf)!="lo"):
            #clear any old queueing disciplines
            switch.cmd("tc qdisc del dev {} root".format(str(intf)))
            device_str = "add dev "+str(intf)
            print switch.cmd("tc qdisc "+device_str+" root handle 1: prio bands 16 priomap 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0")
            for i in range(1,17):
                #add bandwidth limit
                switch.cmd("tc qdisc {} parent 1:{} handle {}: tbf rate 1000mbit buffer 1600 limit 5000".format(device_str, hex(i), hex(i+10)))

                #add delay 
                delay = "6us"
                print switch.cmd("tc qdisc {} parent {}:1 handle {}: netem delay {}".format(device_str, hex(i+10), i+20, delay))

                #start matching at capital 'A' onwards (i.e. 'A' = priority 1, 'P' = priority 16)
                switch.cmd("tc filter {} parent 1:0 protocol ip u32 match u8 {} 0xff at 52 flowid 1:{}".format(device_str, hex(i+64), hex(i)))
                

def addDelayQDisc(switch):
    for intf in switch.intfList():
        if (str(intf)!="lo"):
            #clear any old queueing disciplines
            switch.cmd("tc qdisc del dev {} root".format(str(intf)))
            device_str = "add dev "+str(intf)

            print switch.cmd("tc qdisc "+device_str+" root handle 1: prio bands 16 priomap 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0")
            for i in range(1,17):
                #add bandwidth limit
                switch.cmd("tc qdisc {} parent 1:{} handle {}: tbf rate 1000mbit buffer 1600 limit 5000".format(device_str, hex(i), hex(i+10)))

                #add delay based on priority (low priority = high delay)
                delay = str(i*500) + "ms"
                print switch.cmd("tc qdisc {} parent {}:1 handle {}: netem delay {}".format(device_str, hex(i+10), i+20, delay))

                #start matching at capital 'A' onwards (i.e. 'A' = priority 1, 'P' = priority 16)
                switch.cmd("tc filter {} parent 1:0 protocol ip u32 match u8 {} 0xff at 52 flowid 1:{}".format(device_str, hex(i+64), hex(i)))

def main():
    runstart = time()
    outdir = "%s%s" % (args.out,args.cong)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    workload = ""
    if args.traffic == 'web':
        workload = 'flows/websearch.txt'
    else:
        workload = 'flows/datamining.txt'

    # Setup topology
    if(args.topo=="fattree"):
        topo = FatTree(args.kary)
    else:
        topo = StarTopo(args.hosts)
    net = Mininet(topo=topo,link=TCLink)
    net.start()


    switch = net.get('s0')
    addDelayQDisc(switch)

    #debug
    #for intf in switch.intfList():
    #    print switch.cmd("tc qdisc show dev "+str(intf))

    CLI(net)
    #adjustSysSettings(args.cong, args.topo)
    #net.pingAll()

    
#     # Setup routing: If congestion control is mintcp or none, use pfabric
#     # Setup connection sockets
    
#     # Do this in the sender/receiver: Run tests for traffic type and save outputs
#     random.seed(1111)
   
#     newflow = flow(workload)

#     # bin the flow sizes into 16 bins
#     binSize = newflow.maxSize()/16

#     # grab a random flowSize per flow, determine how many flows to send, bin packets into 16 priorities 
    
#     # Testing seed for consistent results 
#     randomflows = []
#     for i in range (10):
#         randomflows.append(newflow.randomSize())
#         print "The chosen flow size is %d" % randomflows[i]
#     print "The average flow size is %d" % newflow.meanSize()
    
#     net.stop()

#     # Plot experimental outputs
    
#     resetSystem()
#     print "Program completed in %.2fs" % (time()-runstart)
if __name__ == '__main__':
    main()
    
