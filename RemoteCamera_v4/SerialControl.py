# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 10:45:24 2020

@author: HP
"""

import serial
import time
import threading
port.close()
port = serial.Serial(port='COM3', baudrate=9600, bytesize=7, parity='E', stopbits=1, timeout=3)

serialcmd = '0deg-001.000-0000.000--000.000-0010'
#serialcmd = 'home0'
#port.write(serialcmd.encode())

#time.sleep(0.5)
#line = port.readline()
#print(line)

#port.close()
time_start = time.time()
def sent():
    for i in range(1):
        serialcmd = '0deg0041.200--000.000-0000.000-0010'
        #serialcmd = 'home0'
        port.timeout = 5
        port.write(serialcmd.encode())
        reading = port.readline(28)
        #time.sleep(0.5)
        print(reading)
    return reading
#        time.sleep(0.5)


#thread = threading.Thread(target=read_from_port, args=(port))
#thread.start()
        
reading = sent()

time_end = time.time()

port.close()

print(time_end - time_start)