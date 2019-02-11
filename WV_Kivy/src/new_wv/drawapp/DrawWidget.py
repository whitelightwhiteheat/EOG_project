import sys
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.window import Window
from kivy.graphics.instructions import InstructionGroup
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'C://Users//Pieter//Documents//Documenten//--- SCHOOL ---//FASE III//WV//eog_project//WV_Kivy//src'))
from new_wv.controller.State import State as EOGState
#import Controller
class DrawWidget(Widget):
    #USB Connection with controller object
    old_position_X = 100
    old_position_Y = 100
    current_position_X = 100
    current_position_Y = 100
    DRAW_LENGTH = 10
    
    state = EOGState.Mid
    boxes = InstructionGroup()
    
    def __init__(self, **kwargs):
        self._keyboard = Window.request_keyboard(self._keyboard_closed,self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        super(DrawWidget,self).__init__(**kwargs)
        self.canvas.add(self.boxes)
        #self.controller = Controller()
        
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
        
    def _on_keyboard_down(self,keyboard,keycode,text,modifiers):
        if(keycode[1] == 'up'):
            self.draw_up()
            self.state = EOGState.Up
        if(keycode[1] == 'left'):
            self.state = EOGState.Left
            self.draw_left()
        if(keycode[1] == 'down'):
            self.state = EOGState.Down 
            self.draw_down()
        if(keycode[1] == 'right'):
            self.draw_right()
            self.state = EOGState.Right 
        self.drawState()
            
    def draw_up(self):
        self.current_position_Y += self.DRAW_LENGTH
        self.drawLine()
        self.setOldPos()
    def draw_left(self):
        self.current_position_X -= self.DRAW_LENGTH
        self.drawLine()
        self.setOldPos()
    def draw_down(self):
        self.current_position_Y -= self.DRAW_LENGTH
        self.drawLine()
        self.setOldPos()
    def draw_right(self):
        self.current_position_X += self.DRAW_LENGTH
        self.drawLine()
        self.setOldPos()
        
    def setOldPos(self):
        self.old_position_X = self.current_position_X
        self.old_position_Y = self.current_position_Y
        
    def drawLine(self):
        with self.canvas:
            Line(points=[self.old_position_X,self.old_position_Y,self.current_position_X,self.current_position_Y],width=5) 
    
    def drawState(self):
        bar_thickness = 30
        if(self.state == EOGState.Up):
            pos = (0,Window.height-bar_thickness)
            size = (Window.width,bar_thickness)
            self.drawBox(pos, size, Color(0,1,1,1))
        if(self.state == EOGState.Left):
            pos = (0,0)
            size = (bar_thickness,Window.height)
            self.drawBox(pos, size, Color(1,0,1,1))
        if(self.state == EOGState.Down):
            pos = (0,0)
            size = (Window.width,bar_thickness)
            self.drawBox(pos, size, Color(1,0,0,1))
        if(self.state == EOGState.Right):
            pos = (Window.width-bar_thickness,0)
            size = (bar_thickness,Window.height)
            self.drawBox(pos, size, Color(0,1,0,1))
        if(self.state == EOGState.Mid):
            self.boxes.clear()
            
    def drawBox(self,pos,size,color):
        self.boxes.clear()
        self.boxes.add(color)
        self.boxes.add(Rectangle(pos=pos, size=size)) 