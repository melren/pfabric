#!/usr/bin/python

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

class StarTopo( Topo ):
    def build(self, n=54):    
        linkopts = dict(bw=1000, delay = '2us')
        switch = self.addSwitch('s0')
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            self.addLink(host, switch, **linkopts)
    
