import matplotlib
matplotlib.use('Agg')
import os
import matplotlib.pyplot as plt
import sys
import numpy as np


from argparse import ArgumentParser

parser=ArgumentParser(description="Makes plots for pFabric experiment")
parser.add_argument('--out', '-o',
            help="Directory where data needed for plotting is stored",
            default="outputs/")
args = parser.parse_args()


# Values needed on plot for each scheme:
# 8 average normalized FCT values, one for each load from 0.1-0.8
loads = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8]
maxdata = 666667
maxweb = 20000
bestFCTs = {}

tcpFCTs = []
mintcpFCTs = []
linerateFCTs = []

""" open all files and get best FCTs for each size within the traffic type """
def getbestFCTsperSize(traffic,cong):
    for i in range(len(loads)):
        filename = "%s%s_%s/load%d.txt" % (args.out,traffic, cong,i+1)
        with open(filename, 'r') as f:
            for l in f.readlines():
                data = ([float(i) for i in str.split(l)])
                if data[0] not in bestFCTs.keys():
                    bestFCTs[data[0]]=data[1]
                else:
                    if data[1] < bestFCTs[data[0]]:
                        bestFCTs[data[0]] = data[1]

""" parses the text files to fill in a list of normalized average FCT for each load for each web traffic type """
def parseFile(traffic,congestions,sizeInterval,avg=True):
    for ctype in congestions:
        flowFCTs = {0.1:[], 0.2:[],0.3:[],0.4:[],0.5:[],0.6:[],0.7:[],0.8:[]}

        for i in sorted(flowFCTs.keys()):
            filename = "%s%s_%s/load%d.txt" % (args.out,traffic, ctype,int(i*10))
            with open(filename, 'r') as f:
                for l in f.readlines():
                    data = ([float(j) for j in str.split(l)])
                    # store if the data is from the right packet size interval
                    if sizeInterval[0] < data[0] <= sizeInterval[1]:
                        normalizedFCT = data[1]/float(bestFCTs[data[0]])
                        flowFCTs[i].append(normalizedFCT)
        # store average or 99th percentile FCT for each load in flowFCTs and save to proper list by scheme
        for load in sorted(flowFCTs.keys()):
            times = flowFCTs[load]

            if avg:
                if ctype == "mintcp":
                    mintcpFCTs.append(np.mean(times))
                if ctype == "tcp":
                    tcpFCTs.append(np.mean(times))
                if ctype == "none":
                    linerateFCTs.append(np.mean(times))
            else:
                if ctype == "mintcp":
                    mintcpFCTs.append(np.percentile(times,99))
                if ctype == "tcp":
                    tcpFCTs.append(np.percentile(times,99))
                if ctype == "none":
                    linerateFCTs.append(np.percentile(times,99))


""" plots data from tcpFCTs, mintcpFCTs, and linerateFCTs and saves to output folder"""
def plotfigs(traffic,interval,avg=True):
    plt.figure()
    avgLabel = 'Avg' if avg else '99th percentile'
    upperLabel = 'KB]' if interval[1]<10000 else 'MB]'
    lowerLabel = ''
    if interval[0] == 10000:
        lowerLabel='MB'
    if interval[0] == 100:
        lowerLabel='KB'
    lowerBound = str(interval[0]) if interval[0]<10000 else '10'
    upperBound = '100'
    if interval[1] == 10000:
        upperBound = '10'
    if interval[1] > 10000:
        upperBound = 'Infinity'
        upperLabel = ')'
    # plot loads vs the right FCT list
    plt.plot(loads, tcpFCTs,color='r',marker='o',ls='solid')
    plt.plot(loads, mintcpFCTs,color='b',marker='s',ls='dashed')
    #plt.plot(loads, linerateFCTs,color='g',marker='^', ls='dotted')
    plt.xlim([0.1,0.8])
    plt.xlabel('Load')
    plt.ylabel('Normalized Flow Completion Time')
    #plt.legend(['TCP + DropTail','MinTCP + pFabric','LineRate + pFabric'], loc='upper left')
    plt.legend(['TCP + DropTail','MinTCP + pFabric'], loc='upper left')
    title = 'Workload: %s (%s%s, %s%s: %s' % (traffic, lowerBound,lowerLabel,upperBound,upperLabel,avgLabel)
    plt.title(title)
    plt.savefig('%s%s_%s_%s_%s.png' % (args.out,traffic, lowerBound,upperBound, avgLabel))
    
    # clear lists after use
    tcpFCTs[:] = []
    mintcpFCTs[:] = []
    linerateFCTs[:] = []

def main():
    traffic = ["data", "web"]
    #cong = ["tcp", "mintcp", "none"]
    cong = ["tcp", "mintcp"]
    
    for t in traffic:
        for c in cong:
            getbestFCTsperSize(t,c)

        maxval = maxdata if t=="data" else maxweb
        subgroups = [[0,maxval],[0,100],[100,10000],[10000,maxval]]

        for interval in subgroups:
            parseFile(t,cong,interval)
            plotfigs(t,interval)
            if interval==[0,100]:
                parseFile(t,cong,interval,avg=False)
                plotfigs(t,interval,avg=False)

        bestFCTs.clear()


if __name__=='__main__':
    main()
