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
class Training:       
    
    
    def getTresholds(self):
        return (self.lTres,self.rTres,self.dTres,self.uTres,self.maxUDTres,self.maxLRTres)
    
    def connect(self):
        self.connectToUSB()

        
        
        self.mAvg = self.getMidAvg()
        self.lTres = self.leftSequence()
        #self.waitForCal()
        self.rTres = self.rightSequence() 
        #self.waitForCal()
        self.dTres = self.downSequence()
        #self.waitForCal()
        self.uTres = self.upSequence() 
        self.maxUDTres = (self.uTres + self.dTres)*self.GAMMA
        self.maxLRTres = (self.lTres + self.rTres)*self.GAMMA

    def leftSequence(self):
        avg = 0
        for x in range(0,3):
            avg += self.getLeftTres(self.mAvg)
        return avg/3
    def rightSequence(self):
        avg = 0
        for x in range(0,3):
            avg += self.getRightTres(self.mAvg)
        return avg/3
    def downSequence(self):
        avg = 0
        for x in range(0,3):
            avg += self.getDownTres(self.mAvg)
        return avg/3
    
    def upSequence(self):
        avg = 0
        for x in range(0,3):
            avg += self.getUpTres(self.mAvg)
        return avg/3
    
    
    def waitForCal(self):
        data = self.endpoint.read(64, 100)
        ch1 = data[0]+data[1]*256
        ch2 = data[2]+data[3]*256
        while(abs(ch1-self.mAvg[1]) > 10 and abs(ch2-self.mAvg[0]) > 10):
            print ("Calibrating...")
            time.sleep(1)
    
    def getMidAvg(self):
        if (self.interact("mid")):
            return self.getTupleAvg(self.getAvgList())
        
    def getLeftTres(self,midAvg):
        if(self.interact("left")):
            avgTup = self.getTupleAvg(self.getAvgList())
            tres = avgTup[0] - midAvg[0]
            return abs(tres)*self.BETA
        
    def getRightTres(self,midAvg):
        if(self.interact("right")):
            avgTup = self.getTupleAvg(self.getAvgList())
            tres = avgTup[0] - midAvg[0]
            return abs(tres)*self.BETA
    def getDownTres(self,midAvg):
        if(self.interact("down")):
            avgTup = self.getTupleAvg(self.getAvgList())
            tres = avgTup[1] - midAvg[1]
            return abs(tres)*self.BETA
        
    def getUpTres(self,midAvg):
        if(self.interact("up")):
            avgTup = self.getTupleAvg(self.getAvgList())
            tres = avgTup[1] - midAvg[1]
            return abs(tres)*self.BETA
         
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
        inp = input ("look " + direction + " and press Enter.")
        if(inp == ""):
            return True
    
    def connectToUSB(self):
        
        self.dev = usb.core.find(idVendor=0x2572, idProduct=0xA001)
        
        reattach = False
        #if dev.is_kernel_driver_active(0):
        #    reattach = True
        #    dev.detach_kernel_driver(0)
        
        self.dev.set_configuration() 
        cfg = self.dev.get_active_configuration() 
        
        interface_number = cfg[(0,0)].bInterfaceNumber 
        alternate_settting = usb.control.get_interface(self.dev, interface_number) 
        intf = usb.util.find_descriptor(cfg, bInterfaceNumber = interface_number, 
                                    bAlternateSetting = alternate_settting) 
        
        self.endpoint = usb.util.find_descriptor(intf,custom_match = \
              lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_IN) 
        
        # This is needed to release interface, otherwise attach_kernel_driver fails 
        # due to "Resource busy"
        usb.util.dispose_resources(self.dev)
        
        # It may raise USBError if there's e.g. no kernel driver loaded at all
        if reattach:
            self.dev.attach_kernel_driver(0)

    def __init__(self):
        self.TIME = 0.5
        self.CNT_LENGTH = 4
        self.BETA = 3/4
        self.GAMMA = 5/4
        thread = threading.Thread(target=self.connect())
        thread.start()
        def signal_handler(signal, frame):
            print("Exitting")
            sys.exit(0)
            signal.signal(signal.SIGINT, signal_handler)
    

       
    

