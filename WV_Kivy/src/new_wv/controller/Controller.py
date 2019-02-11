import sys
from threading import Thread
import time

from BlinkFilter import BlinkFilter
from StateFilter import StateFilter
from USBConnector import USBConnector
from Calibrator import Calibrator
import State as EOGState

sys.path.append('C://Users//Pieter//Documents//Documenten//--- SCHOOL ---//FASE III//WV//eog_project//WV_Kivy//src//new_wv')
KIVY = True
PLOT = False
if(KIVY):
    from training.Kivy_Tester_altered import EOGKivyApp

if(PLOT):
    from plotter import plotter as plt

loopsPerSec = 10

blinkFilterX = None
blinkFilterY = None
stateFilter = None
kivyObj = None
usbconn = None
calibrator = None


def init():
    global kivyObj
    global blinkFilterX
    global blinkFilterY
    global stateFilter
    global usbconn
    global calibrator
    
    blinkFilterX = BlinkFilter()
    blinkFilterY = BlinkFilter()
    stateFilter = StateFilter()
    
    calibrator = Calibrator()
    
    usbconn = USBConnector()
    eogProcess = Thread(target=loop).start()
    if(KIVY):
        kivyObj = EOGKivyApp()
        kivyProcess = Thread(target=kivyObj.run()).start()
        
    
    
            
def loop():
    systime = time.time() * 1000
    
    global kivyObj
    global usbconn
    
    if(PLOT):
        plot = plt(1)
        plot2 = plt(2)

    global blinkFilterX
    global blinkFilterY
    global stateFilter
    
    global calibrator
    
    while True:
        
        signX = usbconn.getXdata()
        signY = usbconn.getYdata()
        normX = blinkFilterX.getFilteredSignal(signX)
        normY = blinkFilterY.getFilteredSignal(signY)
        if(PLOT):
            plot2.draw(signY)
            plot.draw(signX)
        if stateFilter.getState() != EOGState.Calibrating:
            stateFilter.handleSignal(signX,signY)
        else:
            calibrator.calibrate(signX,signY,stateFilter)
        
        if(KIVY):
            kivyObj.draw(stateFilter.getState())
        #EOGState.printState(stateFilter.getState())
        systime = checkTime(systime)
        

def checkTime(previoustime):
    now = time.time()*1000
    timeDiff = now - previoustime
    timeToCheck = (1/loopsPerSec)*1000
    if(timeDiff < timeToCheck):
        time.sleep((timeToCheck - timeDiff)/1000)
    return time.time()*1000

if __name__ == "__main__":
    init()