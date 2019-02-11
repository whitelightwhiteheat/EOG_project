from collections import deque

class BlinkFilter:
    BLINK_COMMAND = 3 #the number of blinks constituting a command
    START_END_DIFFTRES = 50  #Maximaal verschil tussen begin en eind na blink
    MIN_DIFF_TRES = 200     #Minimale uitwijking blink
    START_SIGNAL = 512
    WINDOW_SIZE = 7
    BLINK_COMMAND_WINDOW = 30 #the window in which a sequence of blinks will be recognised as a command
    
    
    def __init__(self):
        self.window = deque()
        self.blinkbuffer = 0 #keep track of the number of blinks within a blink-command-window.
        self.iterationcounter = 0 #keep track of the number of iterations to register when the command window has passed.
        self.counting = False 
        self.initQueue()
        self.maxdif = 0 #variable depicting the difference between the max and average value in the given window.
        self.mindif = 0 #variable depecting the difference between the minimum and average value in the given window.
        self.avg = self.START_SIGNAL
    
    def getFilteredSignal(self,signal):
        self.handleCounting()           
        self.window.appendleft(signal)  #Voeg tij aan window
        output = self.window.pop()      #pop rechts van de queue
        self.updateAvg()
        self.updateMaxDif()       #
        
        Start_end_dif = abs(self.window[0]-self.window[-1])
        #print(Start_end_dif)
        if Start_end_dif < self.START_END_DIFFTRES:
            #print(self.maxdif)
            if self.maxdif > self.MIN_DIFF_TRES:
                self.normaliseWindow(Start_end_dif)
                self.handleBlink()
        return output

    def handleCounting(self):
        if self.iterationcounter > self.BLINK_COMMAND_WINDOW:
            self.iterationcounter = 0
            self.blinkbuffer = 0
            self.counting = False
        if self.counting == True:
            self.iterationcounter = self.iterationcounter+1
        

    def handleBlink(self):
        print("blink!")
        self.blinkbuffer = self.blinkbuffer+1
        if self.blinkbuffer == self.BLINK_COMMAND:
            self.blinkbuffer = 0
            self.handleCommand()
    
    def handleCommand(self):
        #print("command")        ##to be seen
        pass
    
    def normaliseWindow(self,Start_end_dif):
        increment = Start_end_dif/self.WINDOW_SIZE
        for x in range(0,self.WINDOW_SIZE):
            self.window[x] = self.window[0] + increment*x
        self.maxdif = 0

    def initQueue(self):
        for x in range(0,self.WINDOW_SIZE):
            self.window.append(self.START_SIGNAL)


    def updateMinDif(self,signal):
        if signal-self.avg>self.mindif:
            self.mindif = signal - self.avg

    #
    def updateMaxDif(self):
        tempDiff = 0
        for x in self.window:
            if abs(x - self.avg) > tempDiff:
                tempDiff = abs(x - self.avg)
        self.maxdif = tempDiff
    
    def updateAvg(self):
        self.avg = abs(self.window[0]+self.window[-1])/2
        


#Constraints:
    # abs(diff(windows[0], windows[BLINK_LENGTH])) < START_END_DIFFTRES
    #=> abs(diff(window[0],max(window))) > MAX_DIFF_TRES
