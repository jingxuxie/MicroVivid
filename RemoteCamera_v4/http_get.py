# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 16:28:40 2022

@author: 21255
"""

import urllib.request
import time

time_start = time.time()

url = 'http://192.168.122.1:8080/postview/memory/DCIM/100MSDCF/DSC00023.JPG?size=Origin'


for i in range(1):
    contents = urllib.request.urlopen(url).read()

time_end = time.time()
print(time_end - time_start)

local_filename = 'E:/testpostview.jpg'

with open(local_filename, 'wb') as f:
        f.write(contents)
        



