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

import os

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

def adjustSysSettings(cong, topo):
    if(cong!="none"):
        print "Changing TCP and buffer queue size settings..."
        os.system("sudo ./congestion/%s.sh" % cong)
        qSize = 1000
        if(cong=="mintcp"):
            # MTU = 1460 bytes, pFabric qSize = 36864 bytes (36KB)
            qSize = (36864/1460)
        if(cong=="tcp"):
            # TCP-DropTail qSize = 230400 bytes (225KB)
            qSize = (230400/1460)

        if(topo=="star"):
            size = args.hosts

            for n in range(0,size):
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

def main():
    runstart = time()
    outdir = "%s%s" % (args.out,args.cong)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    

    # Setup topology
    if(args.topo=="fattree"):
        topo = FatTree(args.kary)
    else:
        topo = StarTopo(args.hosts)
    net = Mininet(topo=topo,link=TCLink)
    net.start()
    #CLI(net)
    adjustSysSettings(args.cong, args.topo)
    net.pingAll()

    
    # Setup routing: If congestion control is mintcp or none, use pfabric
    # Setup connection sockets
    # Run tests for traffic type and save outputs
   
    net.stop()

    # Plot experimental outputs
    
    resetSystem()
    print "Program completed in %.2fs" % (time()-runstart)
if __name__ == '__main__':
    main()
    
