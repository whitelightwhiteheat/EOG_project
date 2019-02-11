#!/usr/bin/env python
# encoding: utf-8
"""
eogScope.py

Created by Wannes Meert on 16-10-2014.
Copyright (c) 2014 KU Leuven. All rights reserved.
"""

import sys
import argparse
from array import array
import socket
import time
import usb.core
import usb.util
import threading
import signal
#import win32api, win32con
#from win32api import GetSystemMetrics
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line
from kivy.core.window import Window

class MyPaintWidget(Widget):

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            self.togglewriting()


    def update_pos(self, *args):
        if self.writing == True:
            with self.canvas:
                color = (2, 1, 1)
                Color(*color, mode='hsv')
                d = 2.
                Ellipse(pos=(Window.mouse_pos[0], Window.mouse_pos[1]), size=(d, d))

    def __init__(self, **kwargs):
        self.writing = False
        Window.bind(mouse_pos=self.update_pos)
        super(MyPaintWidget, self).__init__(**kwargs)

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
        parent.add_widget(clearbtn)

        def clear_canvas(obj):
            painter.canvas.clear()
        clearbtn.bind(on_release=clear_canvas)

        return parent

    
    PORT = 42001
#HOST = askstring('Scratch Connector', 'IP:')
HOST = "127.0.0.1"
#if not HOST:
  #sys.exit()
scratchSock = None
dev = None
endpoint = None
interface = 0


def connectToUSB():
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

#### ----- GLOBAL VARIABLES ----- ####
MIN_TRESHOLD = 462
MAX_TRESHOLD = 562
# TRESHOLDS
UP_UPPER_TRESHOLD = 80
UP_LOWER_TRESHOLD = 20
DOWN_UPPER_TRESHOLD = -100
DOWN_LOWER_TRESHOLD = -20

MOUSETRACKING = False
MOVEMENT = True

WIDTH = GetSystemMetrics(0)
HEIGHT = GetSystemMetrics(1)

cursorX = (WIDTH/2)
cursorY = (HEIGHT/2)

previous_ch1 = 512
previous_ch2 = 512

state = "MID"

#Average data
avg_ch1_diff = list()
avg_ch2_diff = list()
avg_ch1 = list()
avg_ch2 = list()

#### ----- ________________----- ####
def connect():
    connectToUSB()
    while True:
    #Read from USB
        data = endpoint.read(64, 100)
        ch1 = data[0]+data[1]*256
        ch2 = data[2]+data[3]*256
    
        #avg_calculation
        avg_ch1_diff.append(ch1-previous_ch1)
        avg_ch2_diff.append(ch2-previous_ch2)
        avg_ch1.append(ch1)
        avg_ch2.append(ch2)

# Eye movement translated to XY Coördinates
        if MOUSETRACKING:
            mousetracking(ch1, ch2, cursorX, cursorY)        
            
    # EVENT_BASED Movement
        if (MOVEMENT and len(avg_ch1_diff) >= 1):
            movement()
        time.sleep(0.5)
        
def movement():
    avg1 = sum(avg_ch1)/len(avg_ch1)
    avg2 = sum(avg_ch2)/len(avg_ch2)
    avg_ch1.pop(0)
    avg_ch2.pop(0)
    avg_d1 = sum(avg_ch1_diff)/len(avg_ch1_diff)
    avg_d2 = sum(avg_ch2_diff)/len(avg_ch2_diff)
    avg_ch1_diff.pop(0)
    avg_ch2_diff.pop(0)
    #print (str(avg1) + ";" + str(avg2))
    if(avg_d1 > UP_UPPER_TRESHOLD and avg_d2 < UP_LOWER_TRESHOLD):
        state = get_state(state,"UP")
    if(avg_d1 < DOWN_UPPER_TRESHOLD and avg_d2 > DOWN_LOWER_TRESHOLD):
        state = get_state(state,"DOWN")
    run_state(cursorX,cursorY,state)
            
def mousetracking(ch1,ch2):
    #Treshold for fixation. If there is fixation, dont move
    if (ch1 > MIN_TRESHOLD and ch1 < MAX_TRESHOLD and ch2 > MIN_TRESHOLD and ch2 < MAX_TRESHOLD):
            ch2 = 512
            ch1 = 512
         
    eyeX = ((ch2-512)/1024)*WIDTH
    eyeY = ((ch1-512)/1024)*HEIGHT
    newX = int(0.1*eyeX + cursorX)
    newY = int(0.1*eyeY + cursorY) 
    #win32api.SetCursorPos((newX,newY))
    cursorX = newX
    cursorY = newY

def run_state(x,y,state):
    if(state == "UP"):
        move_up(x,y)
    if(state == "DOWN"):
        move_down(x,y)
    if(state == "MID"):
        print("mid")
    
def move_down(x,y):
    print("down")

def move_up(x,y):
    print("up")
    #win32api.SetCursorPos((int(x+10),int(y)))

def get_state(previous,new):
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

def main(argv=None):
    parser = argparse.ArgumentParser(description='Forward USB input to Scratch')
    #parser.add_argument('--verbose', '-v', action='count', help='Verbose output')
    #parser.add_argument('--flag', '-f', action='store_true', help='Flag help')
    #parser.add_argument('--output', '-o', required=True, help='Output file')
    #parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    #parser.add_argument('input', nargs='+', help='List of input files')
    args = parser.parse_args(argv)
    
    #verbose = args.verbose
    #flag = args.flag
    #output = args.output
    #inputs = args.input
    
    thread = threading.Thread(target=connect)
    thread.start()
  
def signal_handler(signal, frame):
    print("Exitting")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    sys.exit(main())
    MyPaintApp().run()
    


    

