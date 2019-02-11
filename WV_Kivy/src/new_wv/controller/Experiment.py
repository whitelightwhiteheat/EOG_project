import sys
from threading import Thread
import time

from new_wv.controller.BlinkFilter import BlinkFilter
from new_wv.controller.StateFilter import StateFilter
from new_wv.controller.StateFilter2 import StateFilter2
from new_wv.controller.USBConnector import USBConnector
from new_wv.controller.Calibrator import Calibrator
from new_wv.controller.ThresholdTrainer import ThresholdTrainer
sys.path.append('C://Users//Pieter//Documents//Documenten//--- SCHOOL ---//FASE III//WV//eog_project//WV_Kivy//src//new_wv')
import new_wv.controller.State as EOGState
from new_wv.training.Training_2 import Training

from new_wv.training.Kivy_Experiments import ExperimentsApp

loopsPerSec = 10

blinkFilterX = None
blinkFilterY = None
stateFilter1 = None
stateFilter2 = None
stateFilter3 = None
kivyObj = None
usbconn = None
calibrator = None
thresTrainer = None

##Init function creates objects of the needed classes and runs all the threads.
## 1. make objects
## 2. run the mainloop (usb-listener/handler)
## 3. if KIVY parameter is set, run the kivy tester application.
def init():
    global kivyObj
    global blinkFilterX
    global blinkFilterY
    global stateFilter1
    global stateFilter2
    global stateFilter3
    global usbconn
    global calibrator
    global thresTrainer

    blinkFilterY = BlinkFilter()
    ##Instantiates a state filter with a trainer.
    calibrator = Calibrator()
    usbconn = USBConnector()
    training1 = Training(usbconn,200,293,False)
    #training2 = Training(usbconn)
    thresTrainer1 = ThresholdTrainer(training1.vTres,training1.hTres)
    #thresTrainer2 = ThresholdTrainer(training2.vTres,training2.hTres)
    stateFilter1 = StateFilter(150,242)
    stateFilter2 = StateFilter2(thresTrainer1)
    #stateFilter3 = StateFilter2(thresTrainer2)

    kivyObj = ExperimentsApp()
    ##EOG_Proces thread
    Thread(target=loop).start()
    ##KIVY_app thread
    Thread(target=kivyObj.run()).start()

def loop():
    filter = stateFilter2
    systime = time.time() * 1000
    previousTime = time.time()*1000
    global kivyObj
    global usbconn
    global blinkFilterY
    global stateFilter2

    global calibrator

    kivyObj.set_file_name("EOGExp_27-04-2015_TL_1.txt")

    while True:
        signX = usbconn.getXdata()
        signY = usbconn.getYdata()
        normY = blinkFilterY.getFilteredSignal(signY)
        ##If there is no need for calibration handle the signal in the stateFilter.
        ##Else let the calibrator, calibrate the signal.
        if filter.getState() != EOGState.Calibrating:
            filter.handleSignal(signX,normY)
        else:
            calibrator.calibrate(signX,signY,filter)

        ##Experimentseries: use different statefilters for different experiments.
        kivyObj.draw(filter.getState())

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