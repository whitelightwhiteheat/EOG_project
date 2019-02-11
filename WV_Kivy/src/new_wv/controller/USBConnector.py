import sys
import os
print(os.path.exists('C://Users//Pieter//Documents//Documenten//--- SCHOOL ---//FASE III//WV//eog_project//eogScope_py//usb'))
import usb
import usb.core
import usb.util
import threading
import signal
print(usb.core)

#Class for connecting with the EOG device. The device must be configured in the
#following manner to ensure, that the data is in the right format:
##### HEAD CONFIG
# LEFT - RIGHT ==> GREEN - BROWN
# DOWN - UP ==> BLACK - WHITE
##### BOARD CONFIG (The connectors of the board must be turned south)
# BROWN - GREEN - WHITE - BLACK


class USBConnector:
    PORT = 42001
    HOST = "127.0.0.1"
    dev = None
    endpoint = None
    interface = 0
    
    def connectToUSB(self):
        reattach = False
        self.dev = usb.core.find(idVendor=0x2572,idProduct=0xA001)
        self.dev.set_configuration()
        cfg = self.dev.get_active_configuration()
        
        interface_number = cfg[(0,0)].bInterfaceNumber
        alternate_setting = usb.control.get_interface(self.dev, interface_number)
        intf = usb.util.find_descriptor(cfg, bInterfaceNumber = interface_number, bAlternateSetting = alternate_setting)
        self.endpoint = usb.util.find_descriptor(intf,custom_match = \
                lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_IN)
        
        usb.util.dispose_resources(self.dev)

        if reattach:
            self.dev.attach_kernel_driver(0)
    
    def getXdata(self):
        data = self.endpoint.read(64,100)
        return data[2]+data[3]*256
    
    def getYdata(self):
        data = self.endpoint.read(64,100)
        return data[0]+data[1]*256
    
    
            
    def __init__(self):
        thread = threading.Thread(target=self.connectToUSB())
        thread.start()
        def signal_handler(signal, frame):
            print("Exitting")
            sys.exit(0)
            signal.signal(signal.SIGINT, signal_handler) 
            
if __name__ == '__main__':
    conn = USBConnector()
