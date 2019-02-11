from collections import deque
import State as EOGState
from random import randint
class StateFilter:
    
    #######STATE CONSTANTS######
    ###   LEFT_RIGHT           #
    LEFT_MID_TRES = 150         #
    RIGHT_MID_TRES = 150        #
    ###   UP_DOWN              #
    UP_MID_TRES = 150           #
    DOWN_MID_TRES = 150        #
    ######                     #
    #DRIFT_TRES_X = 40          # nog te bepalen
    #DRIFT_TRES_Y = 40          
    ############################
    
    ##Window length is the length of the window in which the differences of the signal are stored
    #This can be useful for fluctuations in the signal (not sure if necessary with blinkfilter)
    WINDOW_SIZE = 10
    
    LR_window = deque()  
    UD_window = deque()
    LR_average = 0 #depreciated
    UD_average = 0
    #General state of the signal
    state = EOGState.Calibrating
    stateX = EOGState.Mid
    stateY = EOGState.Mid
    
    
    
    #Handles the incoming signal and sets the general state accordingly.
    def handleSignal(self,signX,signY):
        
        self.calcXstate_new(signX)
        if(self.stateX == EOGState.Mid):
            self.calcYstate_new(signY)
        #print(EOGState.printState(self.stateX))
        #print(EOGState.printState(self.stateY))
        self.setState()
    
    #Returns the current global state of the signal
    def getState(self):
        return self.state
    
    
    def calcXstate_new(self,sign):
        if(len(self.LR_window) >= self.WINDOW_SIZE):
            self.LR_window.popleft()
            self.LR_window.append(sign)
            diff = self.LR_window[-1] - self.LR_window[0]
            newState = self.stateDiagramX_new(diff)
            if(newState != self.stateX):
                self.LR_window.clear()
                self.stateX = newState
        else:
            self.LR_window.append(sign)
    
    def calcYstate_new(self, sign):
        if(len(self.UD_window) >= self.WINDOW_SIZE):
            self.UD_window.popleft()
            self.UD_window.append(sign)
            diff = self.UD_window[-1] - self.UD_window[0]
            #print(diff)
            newState = self.stateDiagramY_new(diff)
            if(newState != self.stateY):
                self.UD_window.clear()
                self.stateY = newState
        else:
            self.UD_window.append(sign)
    
    
    """
    #Gets the State of the vertical eye movement
    #First it fills up the window and then calculates the
    #average of the window. The difference between the new average and the old
    #average is given to the stateDiagramX method to calculate the new vertical state.
    #if the state is changed, clear the window. A new average will be calculated after this.
    def calcXstate(self,signX):
        if(len(self.LR_window) >= self.WINDOW_SIZE):
            self.LR_window.popleft()
            self.LR_window.append(signX)
            new_avg = self.avg(self.LR_window)
            diff = new_avg - self.LR_average
            newState = self.stateDiagramX(diff)
            if(newState != self.stateX):
                self.LR_window.clear()
                self.stateX = newState
        else:
            self.LR_window.append(signX)
            self.LR_average = self.avg(self.LR_window) 
            
    #Same as calcXstate but for signY
    def calcYstate(self,signY):
        if(len(self.UD_window) > self.WINDOW_SIZE):
            self.UD_window.popleft()
            self.UD_window.append(signY)
            new_avg = self.avg(self.UD_window)
            diff = new_avg - self.UD_average
            newState = self.stateDiagramY(diff)
            if(newState != self.stateY):
                self.UD_window.clear()
                self.stateY = newState
        else:
            self.UD_window.append(signY)
            self.UD_average = self.avg(self.UD_window)
    
    
    """
####### STATE DIAGRAM CALCULATION BASED ON TRESHOLDS #######

    def stateDiagramX_new(self,diff):
        isStateChanged = (diff > self.LEFT_MID_TRES or abs(diff) > self.RIGHT_MID_TRES)
        if(isStateChanged):
            if(self.stateX == EOGState.Right):
                if(abs(diff) > self.LEFT_MID_TRES and diff < 0):
                    return EOGState.Mid
            elif(self.stateX == EOGState.Mid):
                if(diff > self.LEFT_MID_TRES):
                    return EOGState.Right
                if(diff < self.RIGHT_MID_TRES):
                    return EOGState.Left
            elif(self.stateX == EOGState.Left):
                if(diff > self.RIGHT_MID_TRES):
                    return EOGState.Mid
        return self.stateX
    
    def stateDiagramY_new(self,diff):
        isStateChanged = (diff > self.UP_MID_TRES or abs(diff) > self.DOWN_MID_TRES)
        
        if(isStateChanged):
            if(self.stateY == EOGState.Up):
                if(abs(diff) > self.UP_MID_TRES and diff < 0):
                    return EOGState.Mid
            elif(self.stateY == EOGState.Mid):
                if(diff > self.UP_MID_TRES):
                    return EOGState.Up
                if(abs(diff) > self.DOWN_MID_TRES):
                    return EOGState.Down
            elif(self.stateY == EOGState.Down):
                if(diff > self.DOWN_MID_TRES):
                    return EOGState.Mid
        return self.stateY
    """
    def stateDiagramX(self,diff):
        isStateChanged = (diff > self.LEFT_MID_TRES or abs(diff) > self.RIGHT_MID_TRES)
        isDrifted = (abs(diff) > self.DRIFT_TRES_X and not isStateChanged)
        
        if(isDrifted):
            self.state = EOGState.Calibrating
            return
        elif(isStateChanged):
            if(self.stateX == EOGState.Right):
                if(abs(diff) > self.LEFT_MID_TRES and diff < 0):
                    return EOGState.Mid
            elif(self.stateX == EOGState.Mid):
                if(diff > self.LEFT_MID_TRES):
                    return EOGState.Right
                if(diff < self.RIGHT_MID_TRES):
                    return EOGState.Left
            elif(self.stateX == EOGState.Left):
                if(diff > self.RIGHT_MID_TRES):
                    return EOGState.Mid
        return self.stateX
        
    def stateDiagramY(self,diff):
        isStateChanged = (diff > self.UP_MID_TRES or abs(diff) > self.DOWN_MID_TRES)
        isDrifted = (abs(diff) > self.DRIFT_TRES_Y and not isStateChanged)
        
        if(isDrifted):
            self.state = EOGState.Calibrating
            return
        elif(isStateChanged):
            if(self.stateY == EOGState.Up):
                if(abs(diff) > self.UP_MID_TRES and diff < 0):
                    return EOGState.Mid
            elif(self.stateY == EOGState.Mid):
                if(diff > self.UP_MID_TRES):
                    return EOGState.Up
                if(abs(diff) > self.DOWN_MID_TRES):
                    return EOGState.Down
            elif(self.stateY == EOGState.Down):
                if(diff > self.DOWN_MID_TRES):
                    return EOGState.Mid
        return self.stateY
    """
    #Calculate the general state according the X and Y states. A valid state can only
    #occur when either one of the X and Y states are Mid
    def setState(self):
        if(self.stateX == EOGState.Mid):
            if(self.stateY == EOGState.Down):
                self.state = EOGState.Down
            elif(self.stateY == EOGState.Up):
                self.state = EOGState.Up
            else:
                self.state = EOGState.Mid
        elif(self.stateY == EOGState.Mid):
            if(self.stateX == EOGState.Left):
                self.state = EOGState.Left 
            elif(self.stateX == EOGState.Right):
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
    def __init__(self,xThres=161,yThres=242):
        self.DOWN_MID_TRES = yThres
        self.UP_MID_TRES = yThres
        self.RIGHT_MID_TRES = xThres
        self.LEFT_MID_TRES = xThres

if __name__ == '__main__':
    test = StateFilter()
    for x in range(0,100):
        test.handleSignal(randint(0,1000), randint(0,1000))
        print(test.getState())
