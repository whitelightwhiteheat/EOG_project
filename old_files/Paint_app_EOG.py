import sys
import argparse
from array import array
import socket
import time
import usb.core
import usb.util
import threading
import signal
from collections import deque
from random import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line
from kivy.core.window import Window

class MyPaintWidget(Widget):
    PORT = 42001
    HOST = "127.0.0.1"
######################## USB-CONNECTION #########################
    def connectToUSB(self):
        global dev
        global endpoint
        dev = usb.core.find(idVendor=0x2572, idProduct=0xA001)        
        reattach = False
        #if dev.is_kernel_driver_active(0):
        #    reattach = True
        #    dev.detach_kernel_driver(0)
  
        dev.set_configuration() 
        cfg = dev.get_active_configuration() 
  
        interface_number = cfg[(0,0)].bInterfaceNumber 
        alternate_settting = usb.control.get_interface(dev, interface_number) 
        intf = usb.util.find_descriptor(cfg, bInterfaceNumber = interface_number, 
                              bAlternateSetting = alternate_settting) 
  
        endpoint = usb.util.find_descriptor(intf,custom_match = \
            lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_IN) 
  
        # This is needed to release interface, otherwise attach_kernel_driver fails 
        # due to "Resource busy"
        usb.util.dispose_resources(dev)
  
  # It may raise USBError if there's e.g. no kernel driver loaded at all
        if reattach:
            dev.attach_kernel_driver(0)
            
#### CAPTURE USB INPUT :==>: MAIN LOOP #### 
    def connect(self):
        #TRESHOLDS FOR EYEMOVEMENT
        global LOW_LR_TRES
        global UP_LR_TRES
        global MAX_LR_TRES
        global LOW_UD_TRES
        global UP_UD_TRES
        global MAX_UD_TRES
        
        #RUN PARAMETERS
        STATE_MOVEMENT = True
        TRAINING = False
        
        if (TRAINING):
            print(train.getTresholds())
            tresholds = train.getTresholds()
            LOW_LR_TRES = tresholds[0]
            UP_LR_TRES = tresholds[1]
            MAX_LR_TRES = tresholds[4]
            LOW_UD_TRES = tresholds[2]
            UP_UD_TRES = tresholds[3]
            MAX_UD_TRES = tresholds[5]
        else:
            LOW_LR_TRES = 63
            UP_LR_TRES = 80
            MAX_LR_TRES = 179
            LOW_UD_TRES = 100
            UP_UD_TRES = 113
            MAX_UD_TRES = 370
        self.connectToUSB()
        
        SLOPE = 5.5
        
        SCR_WIDTH = 1920
        SCR_HEIGHT = 1080
        
        cursorX = (SCR_WIDTH/2)
        cursorY = (SCR_HEIGHT/2)
        
        #Average data
        avg_list_ch1 = list()
        avg_value_ch1 = 0
        sub_avg_ch1 = deque()
        sub_avg_value_ch1 = 0
        avg_list_ch2 = list()
        avg_value_ch2 = 0
        sub_avg_ch2 = deque()
        sub_avg_value_ch2 = 0
        
        #DEFAULT STATES
        global stateY 
        global stateX
        stateY = "MID"
        stateX = "MID"
        #MAIN LOOP
        while True:
        
            #Read from USB
            if(TRAINING):
                data = train.endpoint.read(64, 100)
            else:
                data = endpoint.read(64,100) 
            
            ch1 = data[0]+data[1]*256
            ch2 = data[2]+data[3]*256
                
            #STATE_BASED BEWEGING BEPALEN
            if(len(sub_avg_ch1) < 5):
                sub_avg_ch1.append(ch1)
            else:
                #fifo queue : deque : Collections package
                #hi-pass scipy.org (Blinks herkennen / filteren)
                sub_avg_ch1.popleft()
                sub_avg_ch1.append(ch1)
                sub_avg_value_ch1 = sum(sub_avg_ch1)/len(sub_avg_ch1)
                avg_list_ch1.append(sub_avg_value_ch1)
                avg_value_ch1 = sum(avg_list_ch1)/len(avg_list_ch1)
                new_state = self.calc_state(stateY,(sub_avg_value_ch1-avg_value_ch1))
                if(new_state != stateY):
                  avg_list_ch1.clear()
                  sub_avg_ch1.clear()
                  stateY = new_state
                self.run_state(0,0,stateY)

            if(len(sub_avg_ch2) < 5):
                sub_avg_ch2.append(ch2)
            else:
                sub_avg_ch2.popleft()
                sub_avg_ch2.append(ch2)
                sub_avg_value_ch2 = sum(sub_avg_ch2)/len(sub_avg_ch2)
                avg_list_ch2.append(sub_avg_value_ch2)
                avg_value_ch2 = sum(avg_list_ch2)/len(avg_list_ch2)
                new_state2 = self.calc_state2(stateX,(sub_avg_value_ch2-avg_value_ch2))
                if(new_state2 != stateX):
                  avg_list_ch2.clear()
                  sub_avg_ch2.clear()
                  stateX = new_state2
                self.run_state(0,0,stateX)
    
            time.sleep(0.1)
            
    def run_state(self,x,y,state):
        if(state == "UP"):
            draw_up()
        if(state == "DOWN"):
            draw_down()
        if(state == "MID"):
            print("mid")
        if(state == "RIGHT"):
            draw_right()
        if(state == "LEFT"):
            draw_left()
            
            
            
    def calc_state(self,state,diff):
        if(diff > UP_UD_TRES or abs(diff) > LOW_UD_TRES):
          if(state == "UP"):
            if(abs(diff) > UP_UD_TRES and diff < 0 and abs(diff) < (MAX_UD_TRES)):
              return "MID"
            if(abs(diff) > MAX_UD_TRES and diff < 0):
              return "DOWN"
          if(state == "MID"):
            if(diff > UP_UD_TRES):
              return "UP"
            if(diff < LOW_UD_TRES):
              return "DOWN"
          if(state == "DOWN"):
            if(diff > 0 and diff > LOW_UD_TRES and diff < MAX_UD_TRES):
              return "MID"
            if(diff > 0 and diff > MAX_UD_TRES):
              return "UP"
          else:
            return "MID"
        else:
          return state
    
    
    def calc_state2(self, state,diff):
        if(diff > UP_LR_TRES or abs(diff) > LOW_LR_TRES):
          if(state == "RIGHT"):
            if(abs(diff) > UP_LR_TRES and diff < 0 and abs(diff) < (MAX_LR_TRES)):
              return "MID"
            if(abs(diff) > MAX_LR_TRES and diff < 0):
              return "LEFT"
          if(state == "MID"):
            if(diff > UP_LR_TRES):
              return "RIGHT"
            if(diff < LOW_LR_TRES):
              return "LEFT"
          if(state == "LEFT"):
            if(diff > 0 and diff > LOW_LR_TRES and diff < MAX_LR_TRES):
              return "MID"
            if(diff > 0 and diff > MAX_LR_TRES):
              return "RIGHT"
          else:
            return "MID"
        else:
          return state
    
    def get_state(self,previous,new):
        if(previous == "DOWN" and new == "UP"):
          return "MID"
        if(previous == "MID" and new == "UP"):
          return "UP"
        if(previous == "MID" and new == "DOWN"):
          return "DOWN"
        if(previous == "UP" and new == "DOWN"):
          return "MID"
        else:
          return "MID"
    ############################## KIVY GUI #########################
    old_position_X = 100
    old_position_Y = 100
    current_position_X = 100
    current_position_Y = 100
    DRAW_LENGTH = 10
    
    def on_touch_down(self, touch):
        if touch.is_double_tap:
            self.togglewriting()


    def update_pos(self, *args):
        if self.writing == True:
            with self.canvas:
                color = (2, 1, 1)
                Color(*color, mode='hsv')
                d = 5.
                Ellipse(pos=(Window.mouse_pos[0], Window.mouse_pos[1]), size=(d, d))

    def __init__(self, **kwargs):
        self.writing = False
        Window.bind(mouse_pos=self.update_pos)
        self._keyboard = Window.request_keyboard(self._keyboard_closed,self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        super(MyPaintWidget, self).__init__(**kwargs)
        self.connect()

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

    def togglewriting(self):
        if self.writing == True:
            self.writing = False
        else:
            self.writing = True
    
#Drawers
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
class MyPaintApp(App):

    def build(self):
        parent = Widget()
        painter = MyPaintWidget()
        clearbtn = Button(text='Clear')
        parent.add_widget(painter)
        parent.add_widget(clearbtn)

        def clear_canvas(obj):
            painter.canvas.clear()
        clearbtn.bind(on_release=clear_canvas)

        return parent


if __name__ == '__main__':
    from kivy.core.window import Window
    #Window.fullscreen = 'auto'
    MyPaintApp().run()

