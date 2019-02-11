from random import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.window import Window
from kivy.graphics.instructions import InstructionGroup
import math
import time
from random import randint
import sys
sys.path.append('C://Users//Pieter//Documents//Documenten//--- SCHOOL ---//FASE III//WV//eog_project//WV_Kivy//src//new_wv')
import new_wv.controller.State as EOGState

class Point(object):

    def __init__(self, x, y):
        self.X = x
        self.Y = y

    def getX(self):
        return self.X
    
    def getY(self):
        return self.Y

    def distance(self, other):
        dx = self.X - other.X
        dy = self.Y - other.Y
        return math.sqrt(dx**2 + dy**2)
    
##############################################################################     
class Goal_box():
    
    def screen_size(self):
        return (1920, 1080)
    
    def __init__(self,X,Y):
        self.origin = Point(X, Y)
        #mainMonitor = CGDisplayBounds(CGMainDisplayID())
        ##HARDCODED SCREENSIZE !!!
        self.width = Window.width
        self.height = Window.height
        self.goal = self.createRandomPoint()

    def getNrGoals(self):
        return self.nr_goals

    def getGoal(self):
        return self.goal
    
    def getOrigin(self):
        return self.origin

    def createNewGoal(self,X,Y):
        self.origin = Point(X,Y)
        self.goal = self.createRandomPoint()
       
    

    def createRandomPoint(self):
        return Point(randint(0,700),randint(0,500))
    
##############################################################################     
class EOGKivyWidget(Widget):
    
    GOAL_DIAMETER = 100
    
    def draw_goal(self):
        with self.canvas:
            Color(0,1,0)
            Ellipse(pos=(self.goals.getGoal().getX(), self.goals.getGoal().getY()), size=(self.GOAL_DIAMETER, self.GOAL_DIAMETER))
            Ellipse(pos=(self.goals.getOrigin().getX(), self.goals.getOrigin().getY()), size=(2, 2))
        self.starttime = time.time()
            
   
    def update_pos(self, *args):
        pnt = Point(self.goals.getGoal().getX() + self.GOAL_DIAMETER/2, self.goals.getGoal().getY() + self.GOAL_DIAMETER/2)
        if self.writing == True:
            xpos = self.current_position_X
            ypos = self.current_position_Y
            last = self.path[-1]
            with self.canvas:
                Line(points=[last.getX(),last.getY(),xpos,ypos], width=2)
            self.path.append(Point(xpos,ypos))
        if Point(self.current_position_X,self.current_position_Y).distance(pnt)<self.GOAL_DIAMETER/2:
            self.reset_goals()
        

    
    def reset_goals(self):
        manhatten = self.dist_eval()
        self.time_eval(manhatten)
        self.canvas.clear()
        self.canvas.add(self.boxes)
        self.path = [Point(self.current_position_X,self.current_position_Y)]
        self.goals.createNewGoal(self.current_position_X,self.current_position_Y)
        self.draw_goal()

    def __init__(self, **kwargs):
        self._keyboard = Window.request_keyboard(self._keyboard_closed,self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.writing = False
        self.path = []
        super(EOGKivyWidget, self).__init__(**kwargs)
        self.canvas.add(self.boxes)
        self.goals = Goal_box(self.current_position_X,self.current_position_Y)
        self.timeval = []
        self.disteval = []
        self.starttime = 0
    
##### EVALUATION OF A SESSION (stored in timeval & disteval)######
    
    #time it takes to reach the goal (sec) divided by the optimal distance
    def time_eval(self,manhatten_distance):
        duration = time.time() - self.starttime
        self.timeval.append(1-(duration/manhatten_distance)) ##Seconds per distance
    
    #difference between the distance of the path followed, and the manhatten distance.
    def dist_eval(self):
        lastPoint = self.path[-1]
        accum_diff = 0
        for i in range(0,len(self.path)-2):
            accum_diff+=self.path[i].distance(self.path[i+1])
        accum_diff += 10 ##Hardcoded fix. Check later
        manh_x = abs(lastPoint.getX()-self.goals.getOrigin().getX())
        manh_y = abs(lastPoint.getY()-self.goals.getOrigin().getY())
        self.disteval.append(accum_diff/(manh_x + manh_y))
        return (manh_x+manh_y)
    
    def output_eval(self):
        average_timeval = sum(self.timeval)/len(self.timeval)
        average_disteval = sum(self.disteval)/len(self.disteval)
        f = open('EOGTest.txt','w')
        str1 = "distance evaluations: " + str(self.disteval) + '\n'
        str2 = "average distance evaluation: " + str(average_disteval) + '\n'
        str3 = "time evaluations: " + str(self.timeval) + '\n'
        str4 = "average time evaluation: " + str(average_timeval) + '\n'
        f.write(str1)
        f.write(str2)
        f.write(str3)
        f.write(str4)
        print ("normalised distance evaluations: ", self.disteval)
        print ("average normalised distance evaluation: ", average_disteval)
        print ("time/distance evaluations: ", self.timeval)
        print ("average time/distance evaluation: ", average_timeval)
        f.close()
        
##### KEYBOARD FUNCTIONALITY FOR TESTING THE TESTER#####  
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
        
    def _on_keyboard_down(self,keyboard,keycode,text,modifiers):
        if(keycode[1] == 'up'):
            self.draw_up()
        if(keycode[1] == 'left'):
            self.draw_left()
        if(keycode[1] == 'down'):
            self.draw_down()
        if(keycode[1] == 'right'):
            self.draw_right()
        if(keycode[1] == 'r'):
            self.output_eval()
        ## START TESTING WHEN ENTER IS PUSHED ##
        if(keycode[1] == 'enter'):
            self.current_position_X = 200
            self.current_position_Y = 200
            self.togglewriting()
            if self.writing == True:
                self.path = [Point(self.current_position_X,self.current_position_Y)]
                self.goals.createNewGoal(self.current_position_X,self.current_position_Y)
                self.draw_goal()
            if self.writing == False:
                self.canvas.clear()
                self.canvas.add(self.boxes)
        if keycode[1] == "s":
            Window.screenshot(name='screenshot.jpg')
    
    def togglewriting(self):
        if self.writing == True:
            self.writing = False
        else:
            self.writing = True

##### DRAW FUNCTIONS FOR EOG INTEGRATION #####
    writing = False
    current_position_X = 200
    current_position_Y = 200
    DRAW_LENGTH = 10
    
    def draw_up(self):
        self.current_position_Y += self.DRAW_LENGTH
        self.update_pos()
    def draw_left(self):
        self.current_position_X -= self.DRAW_LENGTH
        self.update_pos()

    def draw_down(self):
        self.current_position_Y -= self.DRAW_LENGTH
        self.update_pos()
        
    def draw_right(self):
        self.current_position_X += self.DRAW_LENGTH
        self.update_pos()
    
    def draw_mid(self):
        self.update_pos()
        
    def setOldPos(self):
        self.old_position_X = self.current_position_X
        self.old_position_Y = self.current_position_Y
        
    def drawLine(self):
        with self.canvas:
            Line(points=[self.old_position_X,self.old_position_Y,self.current_position_X,self.current_position_Y],width=5) 
    
    
    ################ FLASHY FEEBACK ############
    boxes = InstructionGroup()
    def drawState(self,state):
        bar_thickness = 30
        if(state == EOGState.Up):
            pos = (0,Window.height-bar_thickness)
            size = (Window.width,bar_thickness)
            self.drawBox(pos, size, Color(0,1,1,1))
        elif(state == EOGState.Left):
            pos = (0,0)
            size = (bar_thickness,Window.height)
            self.drawBox(pos, size, Color(0.5,0.5,0.5,1))
        elif(state == EOGState.Down):
            pos = (0,0)
            size = (Window.width,bar_thickness)
            self.drawBox(pos, size, Color(1,1,0,1))
        elif(state == EOGState.Right):
            pos = (Window.width-bar_thickness,0)
            size = (bar_thickness,Window.height)
            self.drawBox(pos, size, Color(0,1,0,1))
        elif(state == EOGState.Calibrating):
            pos = (Window.width/2 - bar_thickness*3, Window.height/2 - bar_thickness*3)
            size = (bar_thickness*6,bar_thickness*6)
            self.drawBox(pos, size, Color(1,0,0,1))
        elif(state == EOGState.Mid):
            pos = (Window.width/2 - bar_thickness, Window.height/2 - bar_thickness)
            size = (bar_thickness*2,bar_thickness*2)
            self.drawBox(pos, size, Color(1,0,1,1))
        else:
            self.boxes.clear()
            
    def drawBox(self,pos,size,color):
        self.boxes.clear()
        self.boxes.add(color)
        self.boxes.add(Rectangle(pos=pos, size=size)) 
             
##############################################################################     
class EOGKivyApp(App):
    painter = None
    def __init__(self):
        global painter
        painter = EOGKivyWidget()
        Window.fullscreen = True
        super(EOGKivyApp, self).__init__()
        
    def build(self):
        global painter
        parent = Widget()
        #clearbtn = Button(text='Clear')
        parent.add_widget(painter)
        ##parent.add_widget(clearbtn)
            ##def clear_canvas(obj):
        ##painter.canvas.clear()
        ##clearbtn.bind(on_release=clear_canvas)

        return parent

    def draw(self,state):
        global painter
        if (state == EOGState.Up):
            painter.draw_up()
        elif (state == EOGState.Left):
            painter.draw_left()
        elif (state == EOGState.Down):
            painter.draw_down()
        elif (state == EOGState.Right):
            painter.draw_right()
        elif (state == EOGState.Mid):
            painter.draw_mid()
            
        painter.drawState(state)


##############################################################################

    

if __name__ == '__main__':
    from kivy.core.window import Window
    Window.fullscreen = True
    EOGKivyApp().run()

