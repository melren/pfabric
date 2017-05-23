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
		    help="Size of K for fat tree topology, default = 6",
		    type=int,
                    default=6)
parser.add_argument('--hosts', '-n',
		    help="Number of hosts to use for star topology, default = 54",
                    type=int,
		    default=54)

args = parser.parse_args()

def adjustCongCtrl(cong):
    if(cong!="none"):
        print "Changing TCP settings..."
        os.system("sudo ./congestion/%s.sh" % cong)

def resetSystem():
    print "Restoring pre-run system settings..."
    os.system("sudo ./congestion/tcp.sh")
    # Additional reset settings

def main():
    runstart = time()
    outdir = "%s%s" % (args.out,args.cong)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    adjustCongCtrl(args.cong)

    # Setup topology
    # topo = FatTree(args.kary)
    topo = StarTopo(args.hosts)
    net = Mininet(topo=topo,link=TCLink)
    net.start()

    dumpNodeConnections(net.hosts)
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
    
