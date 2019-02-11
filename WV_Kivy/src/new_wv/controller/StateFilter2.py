from collections import deque
import State as EOGState
from random import randint
from new_wv.controller.ThresholdTrainer import ThresholdTrainer
class StateFilter2:

    ##Window size is the length of the window that traverses over the signal to calculate start and end.
    ##It should at least be longer than the length of a blink and can be altered to be more responsive or less responsive to fluctuations in the signal. 
    WINDOW_SIZE = 10
    
    LR_window = deque()  
    UD_window = deque()
    #General state of the signal
    state = EOGState.Calibrating
    stateX = EOGState.Mid
    stateY = EOGState.Mid
    thresTrainer = None
    
    
    #Handles the incoming signal and sets the general state accordingly.
    def handleSignal(self,signX,signY):
        
        self.calcXstate(signX)
        if(self.stateX == EOGState.Mid): ## Niet zeker of dit een goed idee is omdat de Y toestand dan "vast" zou kunnen zitten
            self.calcYstate(signY)
        #print(EOGState.printState(self.stateX))
        #print(EOGState.printState(self.stateY))
        self.setState()
        self.thresTrainer.trainThresholds(self.stateX,self.stateY);
        if(self.stateY == EOGState.U2):
            self.stateY = EOGState.Up
        if(self.stateY == EOGState.D2):
            self.stateY = EOGState.Down
        if(self.stateX == EOGState.R2):
            self.stateX = EOGState.Right
        if(self.stateX == EOGState.L2):
            self.stateX = EOGState.Left

    #Returns the current global state of the signal
    def getState(self):
        return self.state
    
    
    def calcXstate(self,sign):
        if(len(self.LR_window) >= self.WINDOW_SIZE):
            self.LR_window.popleft()
            self.LR_window.append(sign)
            diff = self.LR_window[-1] - self.LR_window[0]
            newState = self.stateDiagramX(diff)
            if(newState != self.stateX):
                self.LR_window.clear()
                self.stateX = newState
                self.thresTrainer.checkRLThres(diff)
        else:
            self.LR_window.append(sign)
    
    def calcYstate(self, sign):
        if(len(self.UD_window) >= self.WINDOW_SIZE):
            self.UD_window.popleft()
            self.UD_window.append(sign)
            diff = self.UD_window[-1] - self.UD_window[0]
            #print(diff)
            newState = self.stateDiagramY(diff)
            if(newState != self.stateY):
                self.UD_window.clear()
                self.stateY = newState
                self.thresTrainer.checkUDThres(diff)
        else:
            self.UD_window.append(sign)
    
    
    
    
    
####### STATE DIAGRAM CALCULATION BASED ON TRESHOLDS #######

    def stateDiagramX(self,diff):
        t = self.thresTrainer
        #If the absolute difference is smaller than the threshold, return the same state as before
        if(abs(diff) <= t.getRLThres()):
            return self.stateX
        
        rightMove = diff > t.getRLThres() #A right move is detected when the difference in signal is bigger than the threshold
        leftMove = abs(diff) > t.getRLThres() and diff < 0 #A left move is detected when the difference in signal is negative but absolute bigger than the threshold.
       
        if(self.stateX == EOGState.Right):
            if(leftMove):
                return EOGState.Mid
            if(rightMove):
                return EOGState.R2 # If the state is already Right and a right move is detected, return R2 state
        elif(self.stateX == EOGState.Mid):
            if(rightMove):
                return EOGState.Right 
            if(leftMove):
                return EOGState.Left
        elif(self.stateX == EOGState.Left):
            if(leftMove):
                return EOGState.L2 #Idem R2
            if(rightMove):
                return EOGState.Mid
      
    
    def stateDiagramY(self,diff):
        t = self.thresTrainer
        #If the absolute difference is smaller than the threshold, return the same state as before
        
        if(abs(diff) <= t.getUDThres()):
            return self.stateY
        
        upMove = diff > t.getUDThres()
        downMove = abs(diff) > t.getUDThres() and diff < 0
        
        if(self.stateY == EOGState.Up):
            if(downMove):
                return EOGState.Mid
            if(upMove):
                return EOGState.U2
        elif(self.stateY == EOGState.Mid):
            if(upMove):
                    return EOGState.Up
            if(downMove):
                    return EOGState.Down
        elif(self.stateY == EOGState.Down):
            if(upMove):
                return EOGState.Mid
            if(downMove):
                return EOGState.D2
        
    
    #Calculate the general state according the X and Y states. A valid state can only
    #occur when either one of the X and Y states are Mid
    def setState(self):
        if self.stateX == EOGState.Calibrating or self.stateY == EOGState.Calibrating:
            self.state = EOGState.Calibrating
            return
        if self.stateX == EOGState.Mid:
            if self.stateY == EOGState.Down:
                self.state = EOGState.Down
            elif self.stateY == EOGState.Up:
                self.state = EOGState.Up
            else:
                self.state = EOGState.Mid
        elif self.stateY == EOGState.Mid:
            if self.stateX == EOGState.Left:
                self.state = EOGState.Left 
            elif self.stateX == EOGState.Right:
                self.state = EOGState.Right 
            else:
                self.state = EOGState.Mid
        else:
            self.state = EOGState.Calibrating
    
    def setCalibrated(self):
        self.state = EOGState.Mid
        self.stateX = EOGState.Mid 
        self.stateY = EOGState.Mid   
        
      
    def avg(self,list):
          return sum(list)/len(list)
      
    #Constructor can be used later to pass other tresholds
    def __init__(self,trainer):
        self.thresTrainer = trainer

