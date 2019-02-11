from collections import deque
import sys
import argparse
from array import array
import socket
import time
import usb.core
import usb.util
import threading
import signal
import matplotlib.pyplot as plt
import time

class Training:
    
    WINDOW_SIZE = 10
    SEQUENCE_TIME = 10
    FRACTION = 0.5
        
    LR_average = 0 #depreciated
    UD_average = 0
    
    
    def getTresholds(self):
        return (self.hTres,self.vTres)
    
    def connect(self):
        self.leftSequence()
        lTres = self.getTres()
        self.rightSequence()
        rTres = self.getTres()
        self.hTres = (lTres+rTres)/2
        self.downSequence()
        dTres = self.getTres()
        self.upSequence()
        uTres = self.getTres()
        self.vTres = (dTres+uTres)/2
        print (self.hTres, self.vTres)


    def leftSequence(self):
        self.window = deque()
        self.difs = []
        if(self.interact("left")):
            self.fillWindowH()
            t = time.time()
            systime = time.time()
            while(time.time()-t<self.SEQUENCE_TIME):
                systime = self.checkTime(systime)
                self.lDif()
                
    def rightSequence(self):
        self.window = deque()
        self.difs = []
        if(self.interact("right")):
            self.fillWindowH()
            t = time.time()
            systime = time.time()
            while(time.time()-t<self.SEQUENCE_TIME):
                systime = self.checkTime(systime)
                self.rDif()

    def downSequence(self):
        self.window = deque()
        self.difs = []
        if(self.interact("down")):
            self.fillWindowV()
            t = time.time()
            systime = time.time()
            while(time.time()-t<self.SEQUENCE_TIME):
                systime = self.checkTime(systime)
                self.dDif()

    def upSequence(self):
        self.window = deque()
        self.difs = []
        if(self.interact("up")):
            self.fillWindowV()
            t = time.time()
            systime = time.time()
            while(time.time()-t<self.SEQUENCE_TIME):
                systime = self.checkTime(systime)
                self.uDif()

    def lDif(self):
        dif = self.window[-1] - self.window[-0]
        if(dif < 0):
            self.difs.append(abs(dif))
        self.window.popleft()
        self.window.append(self.connector.getXdata())
    
    def rDif(self):
        dif = self.window[-1] - self.window[0]
        if(dif > 0):
            self.difs.append(abs(dif))
        self.window.popleft()
        self.window.append(self.connector.getXdata())
    
    def dDif(self):
        dif = self.window[-1] - self.window[0]
        if(dif < 0):
            self.difs.append(abs(dif))
        self.window.popleft()
        self.window.append(self.connector.getYdata())

    def uDif(self):
        dif = self.window[-1] - self.window[0]
        if(dif > 0):
            self.difs.append(abs(dif))
        self.window.popleft()
        self.window.append(self.connector.getYdata())


    def fillWindowV(self):
        while(len(self.window)<self.WINDOW_SIZE):
            self.window.append(self.connector.getYdata())

    def fillWindowH(self):
        while(len(self.window)<self.WINDOW_SIZE):
            self.window.append(self.connector.getXdata())


    def waitForCal(self):
        data = self.endpoint.read(64, 100)
        ch1 = data[0]+data[1]*256 #vertical
        ch2 = data[2]+data[3]*256 #horizontal
        while(abs(ch1-self.mAvg[1]) > 10 and abs(ch2-self.mAvg[0]) > 10):
            print ("Calibrating...")
            time.sleep(1)
    
        
    def getTres(self):
        self.difs.sort()
        l = self.difs[0]
        h = self.difs[-1]
        f = (h-l)*(1-self.FRACTION) + l
        t = 0
        i = 0
        for x in self.difs:
            if(x>=f):
                t += x
                i += 1
        return t/i
         
    def getTupleAvg(self,tupList):
        xAvg = 0
        yAvg = 0
        for tup in tupList:
            xAvg += tup[0]
            yAvg += tup[1]
        xAvg = xAvg / len(tupList)
        yAvg = yAvg / len(tupList)
        return (xAvg,yAvg)
               
    def getAvgList(self):
        cnt = 0
        avg_list = list()
        while(cnt < self.CNT_LENGTH):
            data = self.endpoint.read(64, 100)
            ch1 = data[0]+data[1]*256
            ch2 = data[2]+data[3]*256
            tup = (ch2,ch1)
            avg_list.append(tup)
            cnt += 1
            time.sleep(self.TIME)
        return avg_list
       
    def interact(self,direction):
        inp = input ("look " + direction + " and mid alternately, press Enter to start.")
        if(inp == ""):
            return True

    def __init__(self, connector,xTres=0,yTres=0,train=True):
        if(train):
            self.connector = connector
            self.loopsPerSec = 10;
            self.connect()
        else:
            self.vTres = yTres
            self.hTres = xTres


    def checkTime(self, previoustime):
        now = time.time()*1000
        ##timeDiff is the difference between the start of the loop() and the end of it.
        timeDiff = now - previoustime
        timeToCheck = (1/self.loopsPerSec)*1000
        ##if the timeDiff is smaller than the time needed for one loop (specified in loopspersec)
        ##it will sleep until the needed time is passed.
        if(timeDiff < timeToCheck):
            time.sleep((timeToCheck - timeDiff)/1000)
        ##Return the current system time.
        return time.time()*1000

       
    

