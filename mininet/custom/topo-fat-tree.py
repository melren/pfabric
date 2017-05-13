"""FatTree topology by Howar31

Configurable K-ary FatTree topology
Only edit K should work

OVS Bridge with Spanning Tree Protocol

Note: STP bridges don't start forwarding until
after STP has converged, which can take a while!
See below for a command to wait until STP is up.

sudo mn --custom ~/mininet/custom/topo-fat-tree.py --topo fattree --switch ovs-stp
mininet> sh time bash -c 'while ! ovs-ofctl show es_0_0 | grep FORWARD; do sleep 1; done'

Pass '--topo=fattree' from the command line
"""

from mininet.topo import Topo
from mininet.node import OVSSwitch
 
class OVSBridgeSTP( OVSSwitch ):
    """Open vSwitch Ethernet bridge with Spanning Tree Protocol
       rooted at the first bridge that is created"""
    prio = 1000
    def start( self, *args, **kwargs ):
        OVSSwitch.start( self, *args, **kwargs )
        OVSBridgeSTP.prio += 1
        self.cmd( 'ovs-vsctl set-fail-mode', self, 'standalone' )
        self.cmd( 'ovs-vsctl set-controller', self )
        self.cmd( 'ovs-vsctl set Bridge', self,
                  'stp_enable=true',
                  'other_config:stp-priority=%d' % OVSBridgeSTP.prio )
 
switches = { 'ovs-stp': OVSBridgeSTP }

class FatTree( Topo ):

   # def __init__( self ):
    def build( self ):
        # Topology settings
        K = 6                           # K-ary FatTree
        podNum = K                      # Pod number in FatTree
        coreSwitchNum = pow((K/2),2)    # Core switches 
        aggrSwitchNum = ((K/2)*K)       # Aggregation switches
        edgeSwitchNum = ((K/2)*K)       # Edge switches
        hostNum = (K*pow((K/2),2))      # Hosts in K-ary FatTree
        linkopts = dict(bw=10000, delay ='2us')
        
        # Initialize topology
        #Topo.__init__( self )

        coreSwitches = []
        aggrSwitches = []
        edgeSwitches = []

        # Core
        for core in range(0, coreSwitchNum):
            coreSwitches.append(self.addSwitch("cs_"+str(core)))
        # Pod
        for pod in range(0, podNum):
        # Aggregate
            for aggr in range(0, aggrSwitchNum/podNum):
                aggrThis = self.addSwitch("as_"+str(pod)+"_"+str(aggr))
                aggrSwitches.append(aggrThis)
                for x in range((K/2)*aggr, (K/2)*(aggr+1)):
#                    self.addLink(aggrSwitches[aggr+(aggrSwitchNum/podNum*pod)], coreSwitches[x])
                    self.addLink(aggrThis, coreSwitches[x],**linkopts)
        # Edge
            for edge in range(0, edgeSwitchNum/podNum):
                edgeThis = self.addSwitch("es_"+str(pod)+"_"+str(edge))
                edgeSwitches.append(edgeThis)
                for x in range((edgeSwitchNum/podNum)*pod, ((edgeSwitchNum/podNum)*(pod+1))):
                    self.addLink(edgeThis, aggrSwitches[x])
        # Host
                for x in range(0, (hostNum/podNum/(edgeSwitchNum/podNum))):
                    self.addLink(edgeThis, self.addHost("h_"+str(pod)+"_"+str(edge)+"_"+str(x)))

topos = { 'fattree': ( lambda: FatTree() ) }
