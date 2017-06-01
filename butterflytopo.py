from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

from subprocess import Popen, PIPE
from time import sleep, time

import sys
import os


class ButterflyTopo( Topo ):
    def build(self, n=54):    
        linkopts = dict(bw=100, delay = '6us')
        s0 = self.addSwitch('s0')
        s1 = self.addSwitch('s1')

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')

        self.addLink(h1, s0, **linkopts)
        self.addLink(h2, s0, **linkopts)

        self.addLink(s0,s1, **linkopts)
        self.addLink(s1, h3, **linkopts)