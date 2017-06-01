from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from argparse import ArgumentParser
from time import sleep, time
import pickle
from fattopo import FatTree, OVSBridgeSTP
from startopo import StarTopo
from butterflytopo import ButterflyTopo
#from workloads import *
from flows import flow
from sender import Sender
from sender1 import SenderHigh
from sender2 import SenderLow
import os
import random

parser = ArgumentParser(description="Runs experiment")
parser.add_argument('--cong','-c',
            help="Type of congestion control, use: 'tcp', 'mintcp', or 'none'(udp)",
            required=True)
args = parser.parse_args()

def adjustSysSettings(cong):
    print "Changing TCP and buffer queue size settings..."
    os.system("sudo ./congestion/%s.sh>/dev/null" % cong)
    qSize = 1000
    if(cong=="mintcp"):
        # MTU = 1460 bytes, pFabric qSize = 36864 bytes ~ 36KB
        qSize = (36000/1460)
    if(cong=="tcp"):
        # TCP-DropTail qSize = 230400 bytes ~ 225KB
        qSize = (225000/1460)
    
    for j in range(1,4):
        os.system("sudo ifconfig s0-eth{} txqueuelen {}".format(j,qSize))

    for j in range(1,3):
    	os.system("sudo ifconfig s1-eth{} txqueuelen {}".format(j,qSize))

def deleteQDisc(switch):
    for intf in switch.intfList():
        switch.cmd("tc qdisc del dev {} root".format(str(intf)))


def addPriorityQDisc(switch):
    for intf in switch.intfList():
        device_str = "add dev "+str(intf)
        switch.cmd("tc qdisc {} root handle 1: htb default 1".format(device_str))
        switch.cmd("tc class {} parent 1: classid 1:1 htb rate 100mbit ceil 100mbit".format(device_str))
        switch.cmd("tc qdisc "+device_str+" parent 1:1 handle 2: prio bands 16 priomap 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0")
        delay = "6us" 
        for i in range(2,17):
            print switch.cmd("tc qdisc {} parent 2:{} handle {}: netem delay {}".format(device_str, hex(i), hex(i+2), delay))
            #match from 'B'->2 to 'O'->16
            print switch.cmd("tc filter "+device_str+"  parent 2:0 protocol ip u32 match u8 {} 0xff at 52 flowid 2:{}".format(hex(64+i),hex(i)))


def addPriorityQDiscOld(switch):
    for intf in switch.intfList():
        if (str(intf)!="lo"):
            #clear any old queueing disciplines
            switch.cmd("tc qdisc del dev {} root".format(str(intf)))
            device_str = "add dev "+str(intf)
            print switch.cmd("tc qdisc "+device_str+" root handle 1: prio bands 16 priomap 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0")
            for i in range(1,17):
                #add bandwidth limit
                #switch.cmd("tc qdisc {} parent 1:{} handle {}: tbf rate 100mbit buffer 1600 limit 5000".format(device_str, hex(i), hex(i+10)))

                #add delay 
                #delay = "6us"
                #print switch.cmd("tc qdisc {} parent {}:1 handle {}: netem delay {}".format(device_str, hex(i+10), i+20, delay))

                #start matching at capital 'A' onwards (i.e. 'A' = priority 1, 'P' = priority 16)
                switch.cmd("tc filter {} parent 1:0 protocol ip u32 match u8 {} 0xff at 52 flowid 1:{}".format(device_str, hex(i+64), hex(i)))


def resetSystem():
    print "Restoring pre-run system settings..."
    os.system("sudo ./congestion/tcp.sh >/dev/null")

def prioTest():
    topo = ButterflyTopo()
    net = Mininet(topo=topo,link=TCLink)
    net.start()

    adjustSysSettings(args.cong)

    if args.cong!="tcp": #add priority queuing to switch if needed
        switch = net.get('s0')
        deleteQDisc(switch)
        addPriorityQDisc(switch)
        switch = net.get('s1')
        deleteQDisc(switch)
        addPriorityQDisc(switch)

    h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')
    
    largeFlow = 50000
    smallFlow = 2000
 
    h3.popen("sudo python receiver.py {} {} {}".format(8000, args.cong, 10000), shell=True)
    sleep(0.5)

    destList = [h3.IP()]

    sender1 = SenderLow(h1.IP(), "flows/websearch.txt", args.cong, destList)
    with open("sender.pkl", "wb") as f:
    	pickle.dump(sender1, f, -1)
    #print h1.cmd("sudo python sender1.py {}".format(largeFlow))
    sendProc1 = h1.popen("sudo python sender2.py {}".format(largeFlow))

    sleep(0.1)

    sender2 = SenderHigh(h2.IP(), "flows/websearch.txt", args.cong, destList)
    with open("sender.pkl", "wb") as f:
    	pickle.dump(sender2, f, -1)

    sendProc2 = h2.popen("sudo python sender1.py {}".format(largeFlow))

    sendProc1.communicate()
    sendProc2.communicate()
   
    CLI(net)
    net.stop()
    

def main():

    topo = ButterflyTopo()
    net = Mininet(topo=topo,link=TCLink)
    net.start()

    adjustSysSettings(args.cong)

    if args.cong!="tcp": #add priority queuing to switch if needed 
        switch = net.get('s0')
        deleteQDisc(switch) 
        addPriorityQDisc(switch)
        switch = net.get('s1')
        deleteQDisc(switch)
        addPriorityQDisc(switch)

    h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')
    
    largeFlow = 50000
    smallFlow = 2000
 
    h3.popen("sudo python receiver.py {} {} {}".format(8000, args.cong, 10000), shell=True)
    sleep(0.5)

    destList = [h3.IP()]

    sender1 = Sender(h1.IP(), "flows/websearch.txt", args.cong, destList)
    with open("sender.pkl", "wb") as f:
    	pickle.dump(sender1, f, -1)
    #print h1.cmd("sudo python sender.py {}".format(largeFlow))
    sendProc1 = h1.popen("sudo python sender.py {}".format(largeFlow))

    sleep(3)

    sender2 = Sender(h2.IP(), "flows/websearch.txt", args.cong, destList)
    with open("sender.pkl", "wb") as f:
    	pickle.dump(sender2, f, -1)

    sendProc2 = h2.popen("sudo python sender2.py {}".format(smallFlow))

    sendProc1.communicate()
    sendProc2.communicate()
   
    CLI(net)
    net.stop()
    resetSystem()    
if __name__ == '__main__':
    main()
    #prioTest()
    






