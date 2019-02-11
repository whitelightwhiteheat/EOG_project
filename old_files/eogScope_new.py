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
from Training import Training
#import win32api, win32con
#from win32api import GetSystemMetrics
import matplotlib.pyplot as plt
from collections import deque

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



def connect():
  global LOW_LR_TRES
  global UP_LR_TRES
  global MAX_LR_TRES
  global LOW_UD_TRES
  global UP_UD_TRES
  global MAX_UD_TRES
  
  
    
  TEST = False
  PLOT = True
  STATE_MOVEMENT = False
  TRAINING = False

  if (TRAINING):
    train = Training()
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
    connectToUSB()
    
  SLOPE = 5.5
  
  TEST_FILE = "LR_TRES.csv"
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
  
  #MatPlotLib init
  plt.axis([0,100,0,1024])
  xI = 0
  plt.ion()
  x=list()
  y=list()
  plt.show()
  line, = plt.plot(y)

  stateY = "MID"
  stateX = "MID"
  while True:
    
    #Read from USB
    if(TRAINING):
      data = train.endpoint.read(64, 100)
    else:
      data = endpoint.read(64,100) 
    
    ch1 = data[0]+data[1]*256
    ch2 = data[2]+data[3]*256
    
    #PLOT NAAR MATPLOTLIB
    if PLOT:
        x.append(xI)
        y.append(ch2)
        if(xI > plt.xlim()[1]):
          xI = 0
          x=list()
          y=list()
        line.set_ydata(y)
        line.set_xdata(x)
        xI+=1
        plt.draw()
        plt.pause(0.0001)
        output = (str(ch1)+";"+str(ch2) + "\n")
        
    #OUTPUT NAAR CSV BESTAND
    if TEST:
        fh = open("C:/Users/Pieter/Documents/--- SCHOOL ---/FASE III/WV/eog_project/Experimenten/" + TEST_FILE,"a")
        output = (str(ch1)+";"+str(ch2) + "\n")
        fh.write(output)
        fh.close
        #print(output)
        
    #STATE_BASED BEWEGING BEPALEN
    if (STATE_MOVEMENT):
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
        new_state = calc_state(stateY,(sub_avg_value_ch1-avg_value_ch1))
        if(new_state != stateY):
          avg_list_ch1.clear()
          sub_avg_ch1.clear()
          stateY = new_state
        run_state(0,0,stateY)
        
      if(len(sub_avg_ch2) < 5):
        sub_avg_ch2.append(ch2)
      else:
        sub_avg_ch2.popleft()
        sub_avg_ch2.append(ch2)
        sub_avg_value_ch2 = sum(sub_avg_ch2)/len(sub_avg_ch2)
        avg_list_ch2.append(sub_avg_value_ch2)
        avg_value_ch2 = sum(avg_list_ch2)/len(avg_list_ch2)
        new_state2 = calc_state2(stateX,(sub_avg_value_ch2-avg_value_ch2))
        if(new_state2 != stateX):
          avg_list_ch2.clear()
          sub_avg_ch2.clear()
          stateX = new_state2
        run_state(0,0,stateX)
        
    time.sleep(0.1)


def run_state(x,y,state):
  if(state == "UP"):
    move_up(x,y)
  if(state == "DOWN"):
    move_down(x,y)
  if(state == "MID"):
    print("mid")
  if(state == "RIGHT"):
    move_right(x,y)
  if(state == "LEFT"):
    move_left(x,y)
    
def move_down(x,y):
  print("down")

def move_up(x,y):
  print("up")
  
def move_left(x,y):
  print("left")
  
def move_right(x,y):
  print("right")
  

#TRESHOLDS: absolute waarden van de grenzen

def calc_state(state,diff):
  
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
  

def calc_state2(state,diff):
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

if __name__ == "__main__":
    sys.exit(main())

