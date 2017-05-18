#!/usr/bin/python

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from argparse import ArgumentParser
import os

parser = ArgumentParser(description="Runs pFabric Implementation")
parser.add_argument('--out', '-o',
		    help="Directory to store outputs",
		    required=True)
parser.add_argument('--traffic', '-t',
		    help="Web search or datamining traffic",
		    required=True)
parser.add_argument('--cong','-c',
		    help="Type of congestion control: tcp, mintpc, or none(udp)",
		    required=True)
parser.add_argument('--kary', '-k',
		    help="Size of K for fat tree topology, default = 6",
		    type=int,
                    default=6)

args = parser.parse_args()

def setupTopo():
    # setup topology
    os.system("sudo mn --custom mininet/custom/topo-fat-tree.py --topo fattree,%d --link=tc" % (args.kary))


if __name__ == '__main__':
    setupTopo()
