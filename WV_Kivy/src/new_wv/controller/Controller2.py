import sys
from threading import Thread
import time

from new_wv.controller.BlinkFilter import BlinkFilter
from new_wv.controller.StateFilter2 import StateFilter2
from new_wv.controller.USBConnector import USBConnector
from new_wv.controller.Calibrator import Calibrator
from new_wv.controller.ThresholdTrainer import ThresholdTrainer
sys.path.append('C://Users//Pieter//Documents//Documenten//--- SCHOOL ---//FASE III//WV//eog_project//WV_Kivy//src//new_wv')
import new_wv.controller.State as EOGState
from new_wv.training.Training_2 import Training
import os
import os.path

KIVY = False
PLOT = True
TOFILE = True

if(KIVY):
    from new_wv.training.Kivy_Tester_altered import EOGKivyApp

if(PLOT):
    from plotter import plotter as plt


loopsPerSec = 10

blinkFilterX = None
blinkFilterY = None
stateFilter = None
kivyObj = None
usbconn = None
calibrator = None
thresTrainer = None
training = None

##Init function creates objects of the needed classes and runs all the threads.
## 1. make objects
## 2. run the mainloop (usb-listener/handler)
## 3. if KIVY parameter is set, run the kivy tester application.
def init():
    global kivyObj
    global blinkFilterX
    global blinkFilterY
    global stateFilter2
    global usbconn
    global calibrator
    global thresTrainer
    global training

    blinkFilterX = BlinkFilter()
    blinkFilterY = BlinkFilter()
    ##Instantiates a state filter with a trainer.
    calibrator = Calibrator()
    usbconn = USBConnector()
    #training = Training(161, 260)
    training = Training(usbconn,198,242,False)
    #training = Training(usbconn)
    thresTrainer = ThresholdTrainer(training.vTres,training.hTres)
    stateFilter2 = StateFilter2(thresTrainer)


    ##EOG_Proces thread
    Thread(target=loop).start()

    if(KIVY):
        kivyObj = EOGKivyApp()
        ##KIVY_app thread
        Thread(target=kivyObj.run()).start()




def loop():

    systime = time.time() * 1000

    global kivyObj
    global usbconn
    TEST_FILE = "C:/Users/Pieter/Documents/Documenten/--- SCHOOL ---/FASE III/WV/eog_project/Experimenten/paperexperimenten/driftdata.csv"
    if(TOFILE):
        if(not os.path.isfile(TEST_FILE)):
            fh = open(TEST_FILE,"w")
            fh.write("")
            fh.close()
    if(PLOT):
        plot = plt(1)
        plot2 = plt(2)

    global blinkFilterX
    global blinkFilterY
    global stateFilter2

    global calibrator


    while True:

        signX = usbconn.getXdata()
        signY = usbconn.getYdata()
        normX = blinkFilterX.getFilteredSignal(signX)
        normY = blinkFilterY.getFilteredSignal(signY)

        if(TOFILE):
            fh = open(TEST_FILE,"a")
            output = (str(signX)+";"+str(signY) + "\n")
            fh.write(output)
            fh.close
        if(PLOT):
            plot2.draw(signX)
            plot.draw(signY)
        ##If there is no need for calibration handle the signal in the stateFilter.
        ##Else let the calibrator, calibrate the signal.
        if stateFilter2.getState() != EOGState.Calibrating:
            stateFilter2.handleSignal(normX,normY)
        else:
            calibrator.calibrate(normX,normY,stateFilter2)

        if(KIVY):
            kivyObj.draw(stateFilter2.getState())
        #Print the state to the console for debugging purposes
        #EOGState.printState(stateFilter2.getState())
        #Check the system time. This wil wait for the next iteration, based on the loopspersec.
        systime = checkTime(systime)


def checkTime(previoustime):
    now = time.time()*1000
    ##timeDiff is the difference between the start of the loop() and the end of it.
    timeDiff = now - previoustime
    timeToCheck = (1/loopsPerSec)*1000
    ##if the timeDiff is smaller than the time needed for one loop (specified in loopspersec)
    ##it will sleep until the needed time is passed.
    if(timeDiff < timeToCheck):
        time.sleep((timeToCheck - timeDiff)/1000)
    ##Return the current system time.
    return time.time()*1000

if __name__ == "__main__":
    init()