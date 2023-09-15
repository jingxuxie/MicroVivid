# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 16:00:47 2022

@author: 21255
"""

from libsonyapi.camera import Camera_Wifi
from libsonyapi.actions import Actions
import time

camera = Camera_Wifi()  # create camera instance
camera_info = camera.info()  # get camera camera_info
print(camera_info)

print(camera.name)  # print name of camera
print(camera.api_version)


# live_size = camera.do(Actions.setExposureCompensation, param = [-6])
# time.sleep(0.1)
# live_size = camera.do(Actions.setExposureCompensation, param = [6])
# time.sleep(0.1)
# live_size = camera.do(Actions.setExposureCompensation, param = [0])

# camera.do(Actions.setExposureCompensation, param = [0])

# url = camera.do('actTakePicture')
# url = camera.do("awaitTakePicture")

# camera.do("setIsoSpeedRate", param = ['AUTO'])
# camera.do("setExposureCompensation", param = [3])

# url = camera.do("getSupportedPostviewImageSize")

# size = camera.do("getStillSize")



