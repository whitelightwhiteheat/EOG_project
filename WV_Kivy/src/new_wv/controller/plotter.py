import matplotlib.pyplot as plt
class plotter:
        
    def draw(self,data):
        self.x.append(self.xI)
        self.y.append(data)
        
        if(self.xI > plt.xlim()[1]):
            self.xI = 0
            self.x=list()
            self.y=list()
       
        self.line.set_ydata(self.y)
        self.line.set_xdata(self.x)
        self.xI += 1
        plt.draw()
        plt.pause(0.0001)
        
    def __init__(self,nr):
        plt.figure(nr)
        plt.axis([0,100,0,1024])
        self.xI = 0
        plt.ion()
        self.x=list()
        self.y=list()
        plt.show()
        self.line, = plt.plot(self.y)
    """
    def drawTwo(self,data1,data2):
        plt.figure(1)
        self.x.append(self.xI)
        self.y.append(data)
        if(self.xI > plt.xlim()[1]):
            self.xI = 0
            self.x=list()
            self.y=list()
        self.line.set_ydata(self.y)
        self.line.set_xdata(self.x)
        self.xI += 1
        
        plt.subplot(211)
        plt.
"""