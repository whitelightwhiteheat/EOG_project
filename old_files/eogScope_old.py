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
import win32api, win32con
from win32api import GetSystemMetrics
import matplotlib.pyplot as plt
from drawnow import drawnow

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
  #connectToScratch()
  connectToUSB()
   
  test = False
  mousetrack = False
  printe = False
  movement = True

  
  testFile = "Up_mid.csv"
  width = GetSystemMetrics(0)
  height = GetSystemMetrics(1)

  minTreshold = 462
  maxTreshold = 562

  cursorX = (width/2)
  cursorY = (height/2)

  #Average data
  avg_ch1_diff = list()
  avg_ch2_diff = list()
  avg_ch1 = list()
  avg_ch2 = list()

  #MatPlotLib init
  plt.axis([0,100,0,1024])
  xI = 0
  plt.ion()
  x=list()
  y=list()
  plt.show()
  line, = plt.plot(y)
  #ch1 vars
  highest_diff_ch1 = 0
  previous_ch1 = 512
  #ch2 vars
  highest_diff_ch2 = 0
  previous_ch2 = 512

  state = "MID"
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
    
    #Search Highest difference between ch1 values
    new_diff_1 = abs(ch1 - previous_ch1)
    if new_diff_1 > highest_diff_ch1:
      highest_diff_ch1 = new_diff_1
      #print("ch1: " + str(highest_diff_ch1))
    previous_ch1 = ch1

    #Search Highest difference between ch2 values
    new_diff_2 = abs(ch2 - previous_ch2)
    if new_diff_2 > highest_diff_ch2:
      highest_diff_ch2 = new_diff_2
      #print("ch2: " + str(highest_diff_ch2))
    previous_ch2 = ch2

    
    if printe:
        x.append(xI)
        y.append(ch1)
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
        #print(output)
    if test:
        fh = open("C:/Users/Pieter/Documents/--- SCHOOL ---/FASE III/WV/eog_project/Experimenten/" + testFile,"a")
        output = (str(ch1)+";"+str(ch2) + "\n")
        fh.write(output)
        fh.close
        #print(output)
    if mousetrack:
      #Treshold for fixation. If there is fixation, dont move
        if (ch1 > minTreshold and ch1 < maxTreshold and ch2 > minTreshold and ch2 < maxTreshold):
            ch2 = 512
            ch1 = 512
     
        eyeX = ((ch2-512)/1024)*width
        eyeY = ((ch1-512)/1024)*height
        newX = int(0.1*eyeX + cursorX)
        newY = int(0.1*eyeY + cursorY) 
        win32api.SetCursorPos((newX,newY))
        cursorX = newX
        cursorY = newY

    if (movement and len(avg_ch1_diff) >= 1 and len(avg_ch2_diff) >= 1):
      avg1 = sum(avg_ch1)/len(avg_ch1)
      avg2 = sum(avg_ch2)/len(avg_ch2)
      avg_ch1.pop(0)
      avg_ch2.pop(0)
      
      avg_d1 = sum(avg_ch1_diff)/len(avg_ch1_diff)
      avg_d2 = sum(avg_ch2_diff)/len(avg_ch2_diff)
      avg_ch1_diff.pop(0)
      avg_ch2_diff.pop(0)
      #print (str(avg1) + ";" + str(avg2))
      if(avg_d1 > 80 and avg_d2 < 20):
        
        state = get_state(state,"UP")
      if(avg_d1 < -100 and avg_d2 > -20):
        
        state = get_state(state,"DOWN")
        
      run_state(cursorX,cursorY,state)
      #print(avg_d1)
      #print(avg_d2)
    time.sleep(0.5)


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

if __name__ == "__main__":
    sys.exit(main())

