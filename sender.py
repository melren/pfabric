import sys
import struct
import fcntl
import socket
import time
import threading
import random
import pickle
import errno
from flows import flow


class Sender(object):

    def __init__(self, sourceIP, flowSource = "flows/websearch.txt", cong = "mintcp", destList = [], destPort = 8000):
        self.IP = sourceIP
        self.flowSource = flowSource 
        self.destList = destList
        self.destPort = destPort
        self.cong = cong

        self.createPrioMap()
        self.removeSelfFromDestList()

    def removeSelfFromDestList(self):
        dests = []
        for IP in self.destList:
            if IP != self.IP:
                dests.append(IP)
        self.destList = dests

    def createFlowObj(self):
        self.flow = flow(self.flowSource)

    def setTimers(self, st, rt):
        self.starttime = st
        self.runtime = rt

    def createPrioMap(self):
        val = 65
        self.prioMap = {}
        for i in range(1,17):
            self.prioMap[i] = chr(val)
            val += 1

    def openTCPConnection(self, destIP, destPort):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((destIP, destPort))
        return s

    def bindUDPSocket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s

    def pickDest(self):
        random.seed()
        i = random.randrange(len(self.destList))
        dest = self.destList[i]
        return dest

    def getTCPUnacked(self,s):
        fmt = "B"*7+"I"*21
        x = struct.unpack(fmt, s.getsockopt(socket.IPPROTO_TCP, socket.TCP_INFO, 92))
        return int(x[11])

    def sendFlow(self, socket, destIP):
        flowSize = self.flow.randomSize()
        toSend = flowSize
        flowStartTime = time.time()

        while toSend > 0:
            if (time.time() - self.starttime) > self.runtime:
                return None

            priority = self.flow.getPriority(toSend)

            #first byte is the priority, rest of payload is just zeros
            payload = "0"*1023 
            packet = self.prioMap[priority] + payload

            socket.send(packet)
           
            toSend = toSend - 1 #decrement bytes left to send by 1kb

        # numUnacked = self.getTCPUnacked(socket)
        # while (numUnacked > 0):
        #     numUnacked = self.getTCPUnacked(socket)
        #     if (time.time() - self.starttime) > self.runtime:
        #         return None

        FCT = time.time() - flowStartTime
        return (flowSize, flowStartTime, destIP)

    def sendFlowLineRate(self, socket, destIP):
        flowSize = self.flow.randomSize()
        toSend = flowSize
        flowStartTime = time.time()

        while toSend > 0:
            if (time.time() - self.starttime) > self.runtime:
                return None
            
            priority = self.flow.getPriority(flowSize)

            #first byte is the priority, rest of payload is just zeros
            payload = "0"*1023 
            packet = self.prioMap[priority] + payload

            socket.sendto(packet, (destIP, self.destPort))
            toSend = toSend - 1 #decrement bytes left to send by 1kb

            #time.sleep(1/100000.0) #sleep for 10us to send at 100Mbps

        FCT = time.time() - flowStartTime
        return (flowSize, FCT)
            
    def sendRoutine(self):
        destIP = self.pickDest()  #pick random destination
        output = None
        if self.cong != "none":
            s = self.openTCPConnection(destIP, self.destPort)  #open TCP connection to destination
            output = self.sendFlow(s, destIP) #send a random-sized flow to random destination
        else:
            s = self.bindUDPSocket() #create UDP socket
            output = self.sendFlowLineRate(s, destIP) #send a random-sized flow to random destination

        s.close()
        return output


def main():
    hostIP = sys.argv[1]
    workload = sys.argv[2]
    cong = sys.argv[3]
    hostListStr = sys.argv[4]
    load = float(sys.argv[5])
    runtime = float(sys.argv[6])
    output = sys.argv[7]


    random.seed()

    hostList = hostListStr.split(",")
    hostList.pop()

    sender = Sender(hostIP, workload, cong, hostList)
    sender.createFlowObj()

    # #debug; get some member variables
 
    # newflow = sender.flow
    # priomap = sender.prioMap
    
    outfile = "{}/sendlog_load{}.txt".format(output, int(load*10))

    #with open(outfile,"a") as f:  #create new outfile (deletes any old data)
        # f.write("")
        # f.write("Load: " + str(load) +"\n")
        # f.write("Runtime: " + str(runtime) + "\n")
        # f.write("mean flow size: " + str(meanFlowSize) + "\n")
        # f.write("BW: " + str(bw) + "\n")
        # f.write("Flow sizes: " + str(newflow.flowSizes) + "\n")
        # f.write("Flow weights: " + str(newflow.flowWeights) + "\n") 
        # f.write("Prio map: " + str(priomap) + "\n")
        #f.write("Dest List: " + str(sender.destList) + "\n")


    meanFlowSize = (sender.flow).meanSize()
    bw = 0.1 #bw is 0.1Gbps
    #calculate rate (lambda) of the Poisson process representing flow arrivals
    rate = (bw*load*(1000000000) / (meanFlowSize*1000*8.0))
    start = time.time()
    sender.setTimers(start, runtime)
    while (time.time() - start) < runtime:
        #the inter-arrival time for a Poisson process of rate L is exponential with rate L
        waittime = random.expovariate(rate)
        time.sleep(waittime)

        output = sender.sendRoutine()
        if output is not None: 
            flowSize =  output[0]
            flowStartTime = output[1]
            flowStartTime = "{:.4f}".format(flowStartTime);
     
            #result = "{} {}\n".format(flowSize, FCT)
            result = "SEND {} {} {} {}\n".format(sender.IP, output[2], flowSize, flowStartTime)

            #write flowSize and completion time to file named by 'load'
            with open(outfile, "a") as f:
                while True:
                    try:
                        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB) #lock the file
                        break
                    except IOError as e:
                        if e.errno != errno.EAGAIN:                    
                            raise
                        else:
                            time.sleep(0.1)
               
                f.write(result)
                fcntl.flock(f, fcntl.LOCK_UN)

        

if __name__== '__main__':
    main()
    #debug


