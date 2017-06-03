#!/usr/bin/python

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
from flows import flow
from sender import Sender

import os
import random

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
parser.add_argument('--time',
            help="Time for each sender to send flows",
            type=int,
            default=180)
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
if args.time < 60:
    parser.error('Runtime too short')
if args.topo not in ['star','fattree']:
    parser.error('Wrong network topology, use: star or fattree')

def adjustSysSettings(cong, topo):
    if(cong!="none"):
        print "Changing TCP and buffer queue size settings..."
        os.system("sudo ./congestion/%s.sh>/dev/null" % cong)
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
        print "Successfully changed TCP and buffer settings."

def resetSystem():
    print "Restoring pre-run system settings..."
    os.system("sudo ./congestion/tcp.sh >/dev/null")

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

def deleteQDiscs(switch):
    for intf in switch.intfList():
        switch.cmd("tc qdisc del dev {} root".format(str(intf)))

def makeHostList(net):
    hostList = []
    for hostStr in net.keys():
        if "h" in hostStr:
            host = net.get(hostStr)
            hostList.append(host.IP())
    return hostList

def main():
    runstart = time()
    outdir = "%s/%s_%s" % (args.out,args.traffic,args.cong)
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


    adjustSysSettings(args.cong, args.topo)
   
    if args.cong!="tcp": #add priority queuing to switch if needed
        switch = net.get('s0')
        deleteQDiscs(switch)
        addPriorityQDisc(switch)

    #debug
    #for intf in switch.intfList():
    #    print switch.cmd("tc qdisc show dev "+str(intf))

    loadList = [x/10.0 for x in range(1,9)]
    hostList = makeHostList(net) #make list of host IP addresses

    print "Starting experiment with cong={}, workload={}".format(args.cong, args.traffic)

    #start receiver on every host
    for hostStr in net.keys():
        if "h" in hostStr:
            host = net.get(hostStr)
            host.popen("sudo python receiver.py {} {} {}".format(8000, args.cong, args.time), shell=True)

    for load in loadList: 
        print "Running flows for load: {}".format(load)

        #start sender on every host
        senderList = []
        for hostStr in net.keys():
            if "h" in hostStr:
                host = net.get(hostStr)
                sender = Sender(host.IP(), workload, args.cong, hostList)
                with open("sender.pkl", "wb") as f:
                    pickle.dump(sender, f, -1)

                sendProc = host.popen("sudo python sender.py {} {} {} {}".format(load, args.time, outdir, args.hosts))
                senderList.append(sendProc)

        for sendProc in senderList:
            sendProc.communicate()
      
    net.stop()

    
    resetSystem()
    print "Program for congestion control:%s, traffic type:%s completed in %.2fs" % (args.cong, args.traffic,time()-runstart)
if __name__ == '__main__':
    main()
    
