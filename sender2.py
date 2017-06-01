import sys
import fcntl
import socket
import time
import threading
import random
import pickle
from flows import flow


class SenderLow(object):

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

    def sendFlow(self, socket, destIP, flowSize):
        toSend = flowSize
        flowStartTime = time.time()

        while toSend > 0:
            if (time.time() - self.starttime) > self.runtime:
                return None

            priority = 16

            #first byte is the priority, rest of payload is just zeros
            #payload = "0"*1023 
            #packet = self.prioMap[priority] + payload
            packet = "Pthis is a test"
            socket.send(packet)
           
            toSend = toSend - 1 #decrement bytes left to send by 1kb

        FCT = time.time() - flowStartTime
        return (flowSize, FCT)

    def sendFlowLineRate(self, socket, destIP, flowSize):
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

            time.sleep(1/100000.0) #sleep for 10us to send at 100Mbps

        FCT = time.time() - flowStartTime
        return (flowSize, FCT)
            
    def sendRoutine(self):
        destIP = self.pickDest()  #pick random destination
        flowSize = self.flow.randomSize() #pick random flow size

        output = None
        if self.cong != "none":
            s = self.openTCPConnection(destIP, self.destPort)  #open TCP connection to destination
            output = self.sendFlow(s, destIP, flowSize) #send a random-sized flow to random destination
        else:
            s = self.bindUDPSocket() #create UDP socket
            output = self.sendFlowLineRate(s, destIP, flowSize) #send a random-sized flow to random destination

        s.close()
        return output

    def sendRoutineWithSize(self, size):
        destIP = self.pickDest()  #pick random destination
        flowSize = size #pick random flow size

        output = None
        if self.cong != "none":
            s = self.openTCPConnection(destIP, self.destPort)  #open TCP connection to destination
            output = self.sendFlow(s, destIP, flowSize) #send a random-sized flow to random destination
        else:
            s = self.bindUDPSocket() #create UDP socket
            output = self.sendFlowLineRate(s, destIP, flowSize) #send a random-sized flow to random destination

        s.close()
        return output


def debug():
    flowSize = int(sys.argv[1])

    with open("sender.pkl", "rb") as f:
        sender = pickle.load(f)

    sender.createFlowObj()
    start = time.time()
    sender.setTimers(start, 10000)

    outfile = "test.txt"

    for i in range(10):
        startTime = time.time()
        output = sender.sendRoutineWithSize(flowSize)
        if output is not None: 

            flowSize =  output[0]
            FCT = output[1]

            with open(outfile, "a") as f:
                f.write("From {}: Flow size {}: Completed flow number {} with FCT {}\n".format(sender.IP, flowSize, i, FCT))



        

if __name__== '__main__':
    #main()
    debug()


