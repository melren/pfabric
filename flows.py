import random
import os
import math

class flow():
    flowSizes = []
    flowWeights = []
    avgSearchSize = 1620
    avgDataMiningSize = 9500
    flowType = ""

    def __init__(self, filename):
        if(filename not in ["flows/websearch.txt","flows/datamining.txt"]):
            raise ValueError('Incorrect input file')

        flowCDF = []

        with open(filename, 'r') as f:
            for l in f.readlines():
                flowCDF.append(([float(i) for i in str.split(l)]))

        self.flowType = filename.split('.')[0]

        prev = 0
        for size in flowCDF:
            self.flowSizes.append(int(size[0]))
            self.flowWeights.append(size[2]-prev)
            prev = size[2]

    """ This function is taken from http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python/ """
    def weightedChoice(self):
        totals = []
        runningTotal = 0
        
        for w in self.flowWeights:
            runningTotal+=w
            totals.append(runningTotal)

        rnd = random.random()*runningTotal
        for i, total in enumerate(totals):
            if rnd < total:
                return i

    def randomSize(self):
        index = self.weightedChoice()
        return self.flowSizes[index]

    def meanSize(self):
        if self.flowType =="flows/websearch":
            return self.avgSearchSize
        else:
            return self.avgDataMiningSize
        
    def maxSize(self):
        return self.flowSizes[len(self.flowSizes)-1]

    def getPriority(self, flowSize):
        maxSize = self.maxSize()
        #res = math.ceil(math.log(flowSize)/math.log(maxSize)*16)+1
        res = (flowSize / (maxSize / 16)) + 1
        return res if res<=16 else 16

