#!/usr/bin/python

#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI

def setupTopo():
    # setup topology
    sudo mn --custom mininet/custom/topo-fat-tree.py --topo fattree --link=tc

if __name__ == '__main__':
    setupTopo()
