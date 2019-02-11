#this method returns weither the given signal is calibrated or not.


class Calibrator:
    
    MIDDLE_VALUE = 512
    CALIBRATION_INTERVAL = 50 #Nog te bepalen 
    
    def calibrate(self, signX, signY, stateFilter):
        interval = (self.MIDDLE_VALUE - self.CALIBRATION_INTERVAL, self.MIDDLE_VALUE + self.CALIBRATION_INTERVAL)
        inIntervalX = self.isInInterval(signX,interval)
        inIntervalY = self.isInInterval(signY,interval)
        if (inIntervalX and inIntervalY):
            stateFilter.setCalibrated()
    
    def isInInterval(self,signal,interval):
        return interval[0] <= signal <= interval[1]

    #Bedoeld voor later als het calibration interval meegegeven wordt door trainings app 
    def __init__(self,calibrationInterval):
        #self.CALIBRATION_INTERVAL = calibrationInterval
        pass
    def __init__(self):
        pass