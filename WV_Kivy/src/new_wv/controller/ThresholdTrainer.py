import State as EOGState
from collections import deque


def avg(list):
    return sum(list)/len(list)

AVERAGE_PERCENTAGE = 0.75
RESET_PERCENTAGE = 0.80
DELTA = 0.95
QUEUE_LENGTH = 3

class ThresholdTrainer:

    
    def __init__(self,UDThres,RLThres):
        #Can be set if a trainer is used.
        self.UD_Thres = UDThres
        self.RL_Thres = RLThres
        self.UD_avg = deque()
        self.RL_avg = deque()
        self.previousX = EOGState.Mid
        self.preciousY = EOGState.Mid

    def getUDThres(self):
        return self.UD_Thres
    def getRLThres(self):
        return self.RL_Thres
    def correctUD(self):
        self.UD_Thres *= DELTA
    def correctRL(self):
        self.RL_Thres *= DELTA
    def trainThresholds(self,stateX,stateY):
        if stateX == EOGState.R2 or stateX == EOGState.L2:
            self.correctRL()
            print("rl-" + str(self.RL_Thres))
        if(stateY == EOGState.U2 or stateY == EOGState.D2):
            self.correctUD()
            print("ud-" + str(self.UD_Thres))

    def checkRLThres(self,diff):
        if len(self.RL_avg) > QUEUE_LENGTH:
            average = avg(self.RL_avg)
            print("avg rl:" + str(average))
            if self.RL_Thres < (AVERAGE_PERCENTAGE * average):
                self.RL_Thres = (RESET_PERCENTAGE * average)
                self.RL_avg.clear()
                print("rl+" + str(self.RL_Thres))
        else:
            self.RL_avg.append(abs(diff))

    def checkUDThres(self, diff):
        if len(self.UD_avg) > QUEUE_LENGTH:
            average = avg(self.UD_avg)
            print("avg ud:" + str(average))
            if self.UD_Thres < (AVERAGE_PERCENTAGE * average):
                self.UD_Thres = (RESET_PERCENTAGE * average)
                self.UD_avg.clear()
                print("ud+" + str(self.UD_Thres))
        else:
            self.UD_avg.append(abs(diff))

