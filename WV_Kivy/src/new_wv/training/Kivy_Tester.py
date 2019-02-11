from random import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line
from kivy.core.window import Window
from kivy.core.window import Window
import math
from random import randint
from Quartz import CGDisplayBounds
from Quartz import CGMainDisplayID

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

class Goal_box():
    
    def screen_size():
        
        return (mainMonitor.size.width, mainMonitor.size.height)
    
    def __init__(self):
        self.origin = Point(Window.mouse_pos[0], Window.mouse_pos[1])
        mainMonitor = CGDisplayBounds(CGMainDisplayID())
        self.width = mainMonitor.size.width 
        self.height = mainMonitor.size.height 
        self.goal = self.createRandomPoint()

    def getNrGoals(self):
        return self.nr_goals

    def getGoal(self):
        return self.goal
    
    def getOrigin(self):
        return self.origin

    def createNewGoal(self):
        self.origin = Point(Window.mouse_pos[0],Window.mouse_pos[1])
        self.goal = self.createRandomPoint()
       


    def createRandomPoint(self):
        return Point(randint(0,700),randint(0,500))

class MyPaintWidget(Widget):
    
    GOAL_RANGE = 50
    
    

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            self.togglewriting()
            if self.writing == True:
                self.path = [Point(Window.mouse_pos[0],Window.mouse_pos[1])]
                self.goals.createNewGoal()
                self.draw_goal()
            if self.writing == False:
                self.canvas.clear()

    def draw_goal(self):
        with self.canvas:
            Color(0,1,0)
            Ellipse(pos=(self.goals.getGoal().getX(), self.goals.getGoal().getY()), size=(self.GOAL_RANGE, self.GOAL_RANGE))
            Ellipse(pos=(self.goals.getOrigin().getX(), self.goals.getOrigin().getY()), size=(2, 2))


    def update_pos(self, *args):
        if self.writing == True:
            xpos = Window.mouse_pos[0]
            ypos = Window.mouse_pos[1]
            last = self.path[len(self.path)-1]
            with self.canvas:
                Line(points=[last.getX(),last.getY(),xpos,ypos], width=2)
            self.path.append(Point(xpos,ypos))
        if Point(Window.mouse_pos[0],Window.mouse_pos[1]).distance(self.goals.getGoal())<self.GOAL_RANGE:
            self.reset_goals()

    
    def reset_goals(self):
        self.canvas.clear()
        self.path = [Point(Window.mouse_pos[0],Window.mouse_pos[1])]
        self.goals.createNewGoal()
        self.draw_goal()

    def __init__(self, **kwargs):
        self.writing = False
        self.path = []
        Window.bind(mouse_pos=self.update_pos)
        super(MyPaintWidget, self).__init__(**kwargs)
        self.goals = Goal_box()
    

    def togglewriting(self):
        if self.writing == True:
            self.writing = False
        else:
            self.writing = True

class MyPaintApp(App):

    def build(self):
        parent = Widget()
        painter = MyPaintWidget()
        clearbtn = Button(text='Clear')
        parent.add_widget(painter)
        ##parent.add_widget(clearbtn)
            ##def clear_canvas(obj):
        ##painter.canvas.clear()
        ##clearbtn.bind(on_release=clear_canvas)

        return parent


if __name__ == '__main__':
    from kivy.core.window import Window
    Window.fullscreen = True
    MyPaintApp().run()