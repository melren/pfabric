#!/usr/bin/python

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from argparse import ArgumentParser
from fattopo import FatTree

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

args = parser.parse_args()

def adjustCongCtrl(cong):
    if(cong!="none"):
        print "Changing TCP settings..."
        os.system("sudo ./congestion/%s.sh" % cong)

def main():
    outdir = "%s%s" % (args.out,args.cong)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    adjustCongCtrl(args.cong)

    # Setup topology
    topo = FatTree(args.kary)
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    # Setup routing: If congestion control is mintcp or none, use pfabric
    # Setup connection sockets
    # Run tests for traffic type and save outputs
   
    net.stop()

    # Plot experimental outputs

if __name__ == '__main__':
    main()
