# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 16:13:52 2020

@author: HP
"""

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget
import win32gui
import win32api
import win32con
import time
# from pywinauto.controls.win32_controls import EditWrapper, ListBoxWrapper,\
    # ButtonWrapper
import cv2
import numpy as np
from plane_formula import Get_Plane_Para, Get_Z_Position
from layer_search import layer_search
from layer_search_TMD import layer_search_TMD
from layer_search_sjtu import layer_search_sjtu
from layer_search_hbn import layer_search_hbn
import os.path
from auxiliary_func import background_divide, get_folder_from_file
import sys
from PyQt5.QtWidgets import QMessageBox, QApplication
from shutil import copyfile
import serial

class StageThread(QThread):
    stagestop = pyqtSignal(str)
    def __init__(self, pos = [0, 0, 1]):
        super().__init__()
        self.pos = pos
        self.thread_move_pos = [0, 0, 0]
        self.start_time = time.time()
        self.stop_time = time.time()
        self.initUI()
        
        
    def initUI(self):
        self.error = False
        self.serial_port_initial()
        
        
    def serial_port_initial(self):
        try:
            self.port = serial.Serial(port='COM3', baudrate=9600, bytesize=7, parity='E', stopbits=1, timeout=3)
        except:
            print('port busy')
            self.error = True
            port_error = PortError()
            
        else:
            self.serialcmd = '0deg-000.000-0000.000--000.000-0010'
            self.port.timeout = 6
            self.send_and_read()
            if self.pos == [0, 0, 1]:
                self.error = True
                port_error = PortError()
        finally:
            if not self.error:
                self.port.close()
            
        
#    def prior_pause(self):
#        for i in range(200):
#            list_box_text = self.prior_list_box.item_texts()
#            if list_box_text[-1] == 'R':
#                if len(list_box_text) > 100:
#                    try:
#                        win32gui.SendMessage(self.hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
#                        win32gui.SetForegroundWindow(self.hwnd)
#                        left, top, right, bottom = win32gui.GetWindowRect(self.manubar_hwnd)
#                        win32api.SetCursorPos([left + int((right - left)/5*3), top + int((bottom - top)/2)])
#                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
#                        win32api.SetCursorPos([left-10, top-10])
#                        time.sleep(0.05)
#                    except:
#                        print('Can NOT set foreground window of prior')
#                break
#            else:
#                time.sleep(0.02)
#        if i == 199:
#            print('prior pause time out!')
        
#    def run(self):
#        if self.error:
#            self.stop()
#            time.sleep(1)
#        else:
#            self.prior_edit_text.set_text('GR ' + str(self.pos[0]) + ' ' + \
#                                          str(self.pos[1]))
#            win32api.SendMessage(self.prior_edit_text_hwnd, win32con.WM_CHAR, 13, 0)
#            time.sleep(0.1)
#            self.prior_pause()            
#    
#            self.stop()
                
    def run(self):
        x0 = self.thread_move_pos[0]
        y0 = self.thread_move_pos[1]
        z0 = self.thread_move_pos[2]
        self.start_time = time.time()
        if len(self.thread_move_pos) == 4:
            speed = self.thread_move_pos[3]
            self.move_xyz(x0, y0, z0, speed)
        else:
            self.move_xyz(x0, y0, z0)
        
    def pos2str(self, pos):
        sign = 'positive'
        if pos < 0:
            sign = 'negative'
        pos = int(abs(pos))
        
        integer = pos//1000
        digit = pos%1000
        
        integer_str = str(integer)
        digit_str = str(digit)
        
        for i in range(3-len(integer_str)):
            integer_str = '0' + integer_str
            
        for i in range(3-len(digit_str)):
            digit_str = '0' + digit_str
            
        if sign == 'positive':
            pos_str = '0' + integer_str + '.' + digit_str
        elif sign == 'negative':
            pos_str = '-' + integer_str + '.' + digit_str
        
        return pos_str
    
    def find_limit(self, x0, y0, z0):
        if x0 > 0:
            x0 = min(x0, 24990 - self.pos[0])
        else:
            x0 = max(x0, -24990 - self.pos[0])
#        print('##################################')
#        print(y0, self.pos)
        if y0 > 0:
            y0 = min(y0, 23000 - self.pos[1])
        else:
            y0 = max(y0, -23000 - self.pos[1])
#        print(y0, self.pos[1])
#        print('####################################')
        if z0 > 0:
            z0 = min(z0, 3990 - self.pos[2])
        else:
            z0 = max(z0, -3990 - self.pos[2])
        return x0, y0, z0
    
    def move_xyz(self, x0, y0, z0, speed = 10):
        x, y, z = self.find_limit(x0, y0, z0)
        x = self.pos2str(x)
        y = self.pos2str(y)
        z = self.pos2str(z)
        speed_str = str(speed)
        for i in range(2-len(speed_str)):
            speed_str = '0' + speed_str
        try:
            self.port.open()
#            self.port.timeout = int(3*10/speed)
            self.serialcmd = '0deg' + x + '-' + y + '-' + z + '-00' + speed_str
            print(self.serialcmd)
            self.send_and_read()
        except:
            print('port is busy now')
        finally:
            self.port.close()
        
    def restore(self):
        self.terminate()
        time.sleep(1)
        try:
            self.port.open()
            self.serialcmd = 'home0'
            self.port.timeout = 15
            self.send_and_read()
            self.port.timeout = 6
        except:
            print('Error restoring stage.')
        finally:
            self.port.close()
    
    def terminate(self):
        time_interval_min = 0.2
        self.stop_time = time.time()
        delta_t = self.stop_time - self.start_time
        if delta_t < time_interval_min:
            time.sleep(time_interval_min)
        try:
#            self.port.close()
#            self.port.open()
            time.sleep(0.1)
            self.port.timeout = 0
            if not self.port.isOpen():
                self.port.open()
            print('sending stop signal')
            self.serialcmd = 'stop'
            self.send_and_read()
        except:
            print('Error terminating stage')
            self.port.close()
        else:
            self.port.timeout = 3
            self.port.close()
#            self.serialcmd = '0deg0000.000-0000.000-0000.000-0010'
#            try:
#                self.port.write(self.serialcmd.encode())
#            except:
#                self.serialcmd = 'stop'
#                self.send_and_read()
#            else:
#                self.port.timeout = 3
            
            
    def get_pos(self):
        try:
            self.port.open()
            self.serialcmd = '0deg0000.000-0000.000-0000.000-0010'
            self.send_and_read()
        except:
            print('Error getting stage position')
        finally:
            self.port.close()
    
    def send_and_read(self):
        try:
            self.port.write(self.serialcmd.encode())
        except:
            print('Can not sent string to port')
        else:
#            print('successfully sending comand', self.serialcmd)
            self.reading = self.port.readline(28)
            raw_str = str(self.reading)
            print(raw_str)
            if len(self.reading) == 28:
                try:
                    x = int(float(raw_str[2:10]) * 1000)
                except:
                    x = int(float(raw_str[2:9]) * 100)
                y = int(float(raw_str[11:19]) * 1000)
                z = int(float(raw_str[20:28]) * 1000)
                self.pos = [x, y, z]
                print(x, y, z)
      
    def close_port(self):
        self.port.close()
    
    def stop(self):
        print('stage stop')
        self.stagestop.emit('stop')
        
        
class PortError(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        QMessageBox.critical(self, "Port error!", "Can't detect stage port! Please check your "
                                  "connection and try it again.")        
        
        
        
        
class AutoFocusThread(QThread):
    focus_finish = pyqtSignal(str)
    def __init__(self, camera, Fine = False):
        super().__init__()
        self.camera = camera
        self.Fine = Fine
        self.initUI()
        
    def initUI(self):
        self.radiant_mean = []
        self.focus = 0
        self.error = False
        self.stage = StageThread()
        if self.stage.error:
            self.error = True
    
         
                
    def run(self):
        if self.error:
            self.stop()
            time.sleep(1)
        self.gradiant_mean = []
        if self.click_go_height_wait(200):
            self.cal_clearness()
            for i in range(10):
                self.down_coarse()
                self.cal_clearness()
            z = 10 - np.argmax(self.gradiant_mean)
            self.click_go_height_wait(z*40)
        
            
        self.gradiant_mean = []
        if self.click_go_height_wait(40):
            self.cal_clearness()
            for i in range(8):
                self.down_fine()
                self.cal_clearness()
            z = 8 - np.argmax(self.gradiant_mean)
            self.click_go_height_wait(z*10)

        if self.Fine:
            self.gradiant_mean = []
            self.click_go_height_wait(5)
            self.cal_clearness()
            for i in range(5):
                self.down_super_fine()
                self.cal_clearness()
            z = 5 - np.argmax(self.gradiant_mean)
            self.click_go_height_wait(z*2)
        
        try:
            self.height = self.stage.pos[2]
        except:
            print('No position read')
        self.stop()
        
    def cal_clearness(self):
        time.sleep(0.2)
        img = self.camera.last_frame
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(img,cv2.CV_64F)
        self.gradiant_mean.append(np.var(abs(laplacian)))
        
    def up_coarse(self):
#        self.soft_key_1_button.click()
        time.sleep(0.7)
    
    def down_coarse(self):
        try:
            self.stage.move_xyz(0, 0, -40)
        except:
            print('Down coarse error')
#        time.sleep(0.7)
    
    def down_fine(self):
        try:
            self.stage.move_xyz(0, 0, -10)
        except:
            print('Down fine error')
#        time.sleep(0.7)
    
    def down_super_fine(self):
        try:
            self.stage.move_xyz(0, 0, -2)
        except:
            print('NO soft key 4')
#        time.sleep(0.7)
        
    def go_height(self, z):
        if self.error:
            print('focus not checked!')
        else:
            self.stage.move_xyz(0, 0, z)
            '''
            self.bx2_edit.set_text(str(round(abs(z),2)))
#            time.sleep(0.1)
    
#            for i in range(3):
#                position_0 = win32gui.GetWindowText(self.bx2_position_hwnd)
            if z > 0:
                self.up_height_button.click()
            else:
                self.down_height_button.click()
#            time.sleep(0.5)
#                position_1 = win32gui.GetWindowText(self.bx2_position_hwnd)
#                if position_1 != position_0:
#                    break
            '''
    def click_go_height_wait(self, h):
#        position_0 = win32gui.GetWindowText(self.bx2_position_hwnd)
#        try:
        self.stage.move_xyz(0, 0, h)
#        except:
#            print('Go height error')
        '''
        time.sleep(0.5)
        self.go_height(h)
        time.sleep(0.5)
        '''
#        position_1 = win32gui.GetWindowText(self.bx2_position_hwnd)
#        if position_1 != position_0:
#            print ('Go height error!')
#            return False
#        else:
#            return True
        return True

    def stop(self):
        print('focus stop')
        self.focus_finish.emit('stop')

        
        
        
        
        
class Set_Stage_Focus(QThread):
    
    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        self.plane_points = []
        self.initUI()
        self.stage_running = True
        self.autofocus_running = True
        self.error = False
        
    def initUI(self):
        self.stage = StageThread()
        if self.stage.error:
            self.error = True
            return -1
        self.stage.stagestop.connect(self.stage_stop)
        self.autofocus = AutoFocusThread(self.camera)
        self.autofocus.focus_finish.connect(self.autofocus_stop)
    
    
    def stage_stop(self, s):
        if s == 'stop':
            self.stage_running = False
            
    def autofocus_stop(self, s):
        if s == 'stop':
            self.autofocus_running = False
            
    
    def wait_stage(self):
        for i in range(200):
            if not self.stage_running:
                print('wait_stage_finished')
                break
            else:
                time.sleep(0.02)
        if i == 199:
            self.stage.terminate()
            self.stage_running = False
            print('stage move time out!!!')
        
    
    def wait_focus(self):
        for i in range(300):
            if not self.autofocus_running:
                print('wait_focus_finished')
                break
            else:
                time.sleep(0.1)
        if i == 99:
            self.autofocus.terminate()
            self.autofocus_running = False
            print('focus time out!!!')
        
    
        
        
        
class FindFocusPlane(Set_Stage_Focus):
    find_focus_plane_stop = pyqtSignal(str)
    def __init__(self, camera, focus_method = 'Single point', size = '10 mm'):
        super().__init__(camera)
        self.para = [0, 0, 1, 0]
        self.focus_method = focus_method
        self.size = size
        
    def run(self):
        if self.focus_method == 'Single point':
            center = max(0, int(self.size[:-3]) * 500 - 1400)
            self.stage.move_xyz(center, center, 0)
            self.autofocus_running = True
            self.autofocus.start()
            self.wait_focus()
            self.stage.move_xyz(-center, -center, 0)
        else:
            self.plane_points = []
            
            start = max(0, int(self.size[:-3]) * 250 - 1000)
            step = int(self.size[:-3]) * 500
            
            start_point = [start, start]
            self.stage.move_xyz(*start_point, 0)
            
            focus_point_1 = [0, 0]
            self.autofocus_running = True
            self.autofocus.start()
            self.wait_focus()
            self.plane_points.append([focus_point_1[0] + start_point[0],\
                                      focus_point_1[1] + start_point[1],\
                                      self.autofocus.height])
            
            focus_point_2 = [0, step]
            self.stage.move_xyz(*focus_point_2, 0)
            self.autofocus_running = True
            self.autofocus.start()
            self.wait_focus()
            self.plane_points.append([focus_point_2[0] + start_point[0],\
                                      focus_point_2[1] + start_point[1],\
                                      self.autofocus.height])
            
            focus_point_3 = [step, 0]
            self.stage.move_xyz(*focus_point_3, 0)
            self.autofocus_running = True
            self.autofocus.start()
            self.wait_focus()
            self.plane_points.append([focus_point_3[0] + start_point[0],\
                                      focus_point_2[1] + start_point[1],\
                                      self.autofocus.height])
            
            self.para = Get_Plane_Para(*self.plane_points)
            height = Get_Z_Position(0, 0, self.para)
            pos_temp = [-start_point[0] - focus_point_3[0],\
                        -start_point[1] - focus_point_2[1],\
                        height - self.plane_points[2][2]]
            self.stage.move_xyz(*pos_temp)
            
            print(self.plane_points, self.para)
        self.stop()
    
    def stop(self):
        self.find_focus_plane_stop.emit('stop')
        
        
        
class Scan(Set_Stage_Focus):
    scan_stop = pyqtSignal(str)
    def __init__(self, camera, plane_para = [0,0,1,0], magnification = '5x'):
        super().__init__(camera)
        self.plane_para = plane_para
        self.magnification = magnification
        self.rotate_90 = False
        
        self.date = time.strftime("%m-%d-%Y")
        self.month = time.strftime('%m')
        self.day = time.strftime('%d')
        self.year = time.strftime('%Y')
        self.save_folder = 'C:/layer_search/'+self.year+'/'+self.month+'/'+self.day
        if not os.path.isdir(self.save_folder):
            os.makedirs(self.save_folder)
            
        self.save_count_dir = 1
        while os.path.isdir(self.save_folder + '/' + str(self.save_count_dir)):
            self.save_count_dir += 1
        self.save_folder += '/' + str(self.save_count_dir)
        os.makedirs(self.save_folder+ '/raw')
        os.makedirs(self.save_folder+ '/temp')
        os.makedirs(self.save_folder+ '/results')
        self.position_filename = self.save_folder + '/results/position.txt'
        self.save_folder += '/raw'
        
        
        self.save_count = 1
        
        self.index = '00_00-00_00'
        
        self.current_dir = os.path.abspath(__file__).replace('\\','/')
        self.current_dir = get_folder_from_file(self.current_dir)
        self.bk_filename = self.current_dir + 'support_file/background/crop_x5.png'
        self.get_background()
        
        self.capture_still = CaptureStill(self.camera, self.background, self.background_norm,\
                                          self.save_folder, self.date, self.save_count,\
                                          self.index)
        self.capture_still.capture_done.connect(self.recv_capture_done)
        self.capture_still_running = False
        self.threshold = 10000
        
    def run(self):
        self.dark_upper = 70
        self.bright_lower = 100
        if self.magnification == '5x':
            step = 2240
            x_sample = 5
            y_sample = 5
        elif self.magnification == '10x':
            step = 1120
            x_sample = 10
            y_sample = 10
#            self.dark_upper = 100
#            self.bright_lower = 150
            self.bk_filename = self.current_dir + 'support_file/background/crop_x10.png'
            self.get_background()
        elif self.magnification == '20x':
            step = 600
            x_sample = 20
            y_sample = 20
            self.bk_filename = self.current_dir + 'support_file/background/crop_x20.png'
            self.get_background()
        self.scan_matrix = np.zeros((x_sample+1, y_sample+1), dtype = int) + 1
        delta_x = abs(Get_Z_Position(5000, 0, self.plane_para) - \
                      Get_Z_Position(0, 0, self.plane_para))
        delta_y = abs(Get_Z_Position(0, 5000, self.plane_para) - \
                      Get_Z_Position(0, 0, self.plane_para))
        if delta_x > delta_y:
            self.rotate_90 = True
        height = []
        height_accu = 0
        height.append(Get_Z_Position(0, 0, self.plane_para))
        delta_height = 0
        
        while os.path.isfile(self.save_folder+'/'+str(self.save_count)+'-'+self.date+\
                             '-'+'00_00-00_00'+'.jpg'):
            self.save_count += 1
        img_temp = np.zeros((512,512,3), dtype = np.uint8)
        cv2.imwrite(self.save_folder+'/'+str(self.save_count)+'-'+self.date+\
                             '-'+'00_00-00_00'+'.jpg', img_temp)
        
        self.get_index(x_sample, y_sample, 0, 0)
        
        self.capture_save()
        
        for i in range(y_sample+1):
            for j in range(x_sample):
                time_start = time.time()
#                if self.rotate_90:
#                    height.append(Get_Z_Position(i*step, (j+1)*step, self.plane_para))
#                else:
                height.append(Get_Z_Position((j+1)*step, i*step, self.plane_para))
                delta_height = height[-1] - height[-2]
                height_accu += delta_height
                
#                if abs(height_accu) > 3:
#                    self.focus(height_accu)
#                    height_accu = 0
#                    time.sleep(0.1)
                
#                if self.rotate_90:
#                    self.stage.move_xyz(0, step, delta_height)
#                    self.get_index(x_sample, y_sample, i, j+1)
#                else:
                self.stage.move_xyz(step, 0, delta_height)
                self.get_index(x_sample, y_sample, j+1, i)
                ret = self.capture_save()
                print(self.scan_matrix)
                if ret == 'edge':
                    self.scan_matrix[j+1, i] = 0
                    if self.scan_matrix[j, i] == 1 and j >= 1:
                        if self.scan_matrix[j-1, i] == 1:
                            break
                elif ret == 'end':
                    self.scan_matrix[j+1, i] = -1
                    break
                
                time_end = time.time()
                print(time_end - time_start)
                print(i,j)
                print('123')
            print(self.stage.pos)
            if i == y_sample:
                break
            else:
#                print('456')
#                if self.rotate_90:
#                    height.append(Get_Z_Position((i+1)*step, 0, self.plane_para))
#                else:
                height.append(Get_Z_Position(0, (i+1)*step, self.plane_para))
                delta_height = height[-1] - height[-2]
                height_accu += delta_height
                
#                if abs(height_accu) > 3:
#                    self.focus(height_accu)
#                    height_accu = 0
#                    time.sleep(0.1)
                
#                if self.rotate_90:
#                    self.stage.move_xyz(step, -(j+1)*step, delta_height)
#                    self.get_index(x_sample, y_sample, i+1, 0)
#                else:
                self.stage.move_xyz(-(j+1)*step, step, delta_height)
                self.get_index(x_sample, y_sample, 0, i+1)
                ret = self.capture_save()
                if ret == 'end':
                    break
        
        self.stop()
        
#    def move(self, pos = [0, 0]):
#        self.stage_running = True
#        self.stage.pos = pos
#        self.stage.start()
#        self.wait_stage()
    
#    def focus(self, h = 0):
#        self.autofocus.go_height(h)
        
    def recv_capture_done(self, s):
        if s == 'stop':
            print('capture stop')
            self.capture_still_running = False
            self.capture_still.running = False
        
    def capture_save(self):
        for i in range(50):
            self.img_temp = self.camera.last_frame
            gray_1 = cv2.cvtColor(self.img_temp, cv2.COLOR_BGR2GRAY)
            time.sleep(0.04)
            
            self.img = self.camera.last_frame
            gray_2 = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            d_frame = cv2.absdiff(gray_1, gray_2)
            
            if np.sum(d_frame[d_frame > 50]) < self.threshold:
                break
            
        left_crop = int(self.img.shape[1]*0.17)
        right_crop = int(self.img.shape[1]*0.83)
        self.img = self.img[:, left_crop:right_crop]
        self.img = background_divide(self.img, self.background, self.background_norm)
        cv2.imwrite(self.save_folder+'/'+str(self.save_count)+'-'+self.date+\
                    '-'+self.index+'.jpg', self.img)
        ret = self.decide_is_edge()
        self.write_position()
        return ret
        '''
        if not self.capture_still_running or not self.capture_still.running:
            self.capture_still.save_count = self.save_count
            self.capture_still.index = self.index
            self.capture_still.running = True
            self.capture_still_running = True
            self.capture_still.start()
            time.sleep(0.1)
        else:
            print('capture wrong, capture wrong, capture wrong!')
            #time.sleep(0.1)
            #if self.capture_still_running:
            self.capture_still_running = False
                
            self.capture_still.save()
            time.sleep(0.1)
            #else:
            self.capture_still.terminate()
        '''
            
#        img = self.camera.last_frame
#        left_crop = int(img.shape[1]*0.17)
#        right_crop = int(img.shape[1]*0.83)
#        img = img[:, left_crop:right_crop]
#        img = background_divide(img, self.background, self.background_norm)
#
##        while os.path.isfile(self.save_folder+'/'+self.date+'-'+str(self.save_count)+\
##                             '-'+'00_00-00_00'+'.jpg'):
##            self.save_count += 1
#        cv2.imwrite(self.save_folder+'/'+self.date+'-'+str(self.save_count)+\
#                    '-'+self.index+'.jpg', img)
##        self.save_count += 1
    
    def write_position(self):
        with open(self.position_filename, 'a') as file:
            file.write(str(self.save_count)+'-'+self.date+'-'+self.index+'.jpg'+' '\
                       +str(self.stage.pos[0])+' '+str(self.stage.pos[1])+' '+str(self.stage.pos[2]) + '\n')
    
    def decide_is_edge(self):
        img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([img], [0], None, [256], [0,255])
        hist /= np.max(hist)
        hist *= 1000
        dark_peak = np.max(hist[:self.dark_upper])
        bright_peak = np.max(hist[self.bright_lower:])
        if bright_peak < 100:
            return 'end'
        if dark_peak > 100:
            return 'edge'
        return 'normal'
    
    
    def get_index(self, total_x, total_y, x, y):
        size_x = self.int2str(total_x)
        size_y = self.int2str(total_y)
        pos_x = self.int2str(x)
        pos_y = self.int2str(y)
        
        self.index = size_x+'_'+size_y+'-'+pos_x+'_'+pos_y
        
    def int2str(self, num):
        if num > 9:
            return str(num)
        else:
            return '0'+str(num)
    
    def get_background(self):
        self.background = cv2.imread(self.bk_filename)
        self.background_norm = np.zeros(3)
        for i in range(3):
            self.background_norm[i] = np.mean(self.background[:,:,i])
            print(self.background_norm[i])
    
    def stop(self):
        self.scan_stop.emit('stop')
        

class CaptureStill(QThread):
    capture_done = pyqtSignal(str)
    def __init__(self, camera, background, background_norm, save_folder, date, \
                 save_count, index):
        super().__init__()
        self.camera = camera
        self.threshold = 500000
        self.background = background
        self.background_norm = background_norm
        self.save_folder = save_folder
        self.date = date
        self.save_count = save_count
        self.index = index
        self.running = False
        
    def run(self):
        self.running = True
        for i in range(15):
            self.img_temp = self.camera.last_frame
            gray_1 = cv2.cvtColor(self.img_temp, cv2.COLOR_BGR2GRAY)
            time.sleep(0.02)
            
            self.img = self.camera.last_frame
            gray_2 = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            d_frame = cv2.absdiff(gray_1, gray_2)
            
            if np.sum(d_frame[d_frame > 50]) < self.threshold:
                break
            
        left_crop = int(self.img.shape[1]*0.17)
        right_crop = int(self.img.shape[1]*0.83)
        self.img = self.img[:, left_crop:right_crop]
        self.img = background_divide(self.img, self.background, self.background_norm)
        cv2.imwrite(self.save_folder+'/'+self.date+'-'+str(self.save_count)+\
                    '-'+self.index+'.jpg', self.img)
        self.running = False
        self.capture_done.emit('stop')
        print('sum',np.sum(d_frame[d_frame > 50]))

    def save(self):
        left_crop = int(self.img.shape[1]*0.17)
        right_crop = int(self.img.shape[1]*0.83)
        self.img = self.img[:, left_crop:right_crop]
        self.img = background_divide(self.img, self.background, self.background_norm)
        cv2.imwrite(self.save_folder+'/'+self.date+'-'+str(self.save_count)+\
                    '-'+self.index+'.jpg', self.img)
        self.running = False
        self.capture_done.emit('stop')
        


class LayerSearchThread(QThread):
    def __init__(self, thickness = '285nm', material = 'Graphene', filepath = '',\
                 resultpath = '', contrast_range = [0.028, 0.30]):
        super().__init__()
        self.thickness = thickness
        self.material = material
        self.filepath = filepath
        if os.path.isdir(self.filepath):
            self.pathDir =  os.listdir(self.filepath)
            self.pathDir.sort(key= lambda x:int(x[11:-16]))#按数字排序
        else:
            self.pathDir = []
        
        self.outpath = 'C:/temp'
#        self.finishedDir = os.listdir(self.outpath)
        self.finished_count = 0 #len(self.finishedDir)
        
        self.resultpath = resultpath
        
        self.contrast_range = contrast_range
    
    def run(self):
        time_start = time.time()
        record_len = len(self.pathDir)
        #i = 0
        while True:
            if os.path.isdir(self.filepath):
                self.pathDir =  os.listdir(self.filepath)
                self.pathDir.sort(key= lambda x:int(x[11:-16]))#按数字排序
            else:
                self.pathDir = []
            time.sleep(1)
            if len(self.pathDir) != record_len:
                time_start = time.time()
            else:
                time_end = time.time()
                if time_end - time_start > 120:
                    print('layer search finished')
                    break
            for self.finished_count in range(len(self.pathDir)):
                output_name = self.outpath+'/'+self.pathDir[self.finished_count]
                if not os.path.isfile(output_name):
                    input_name = self.filepath+'/'+self.pathDir[self.finished_count]
    #                print(input_name)
                    output_name = self.outpath+'/'+self.pathDir[self.finished_count]
                    result_name = self.resultpath+'/'+self.pathDir[self.finished_count]
                    if self.material == 'Graphene':
                        if self.thickness == 'Bare':
                            ret, img_out = layer_search_sjtu(input_name)
                        else:
                            ret, img_out = layer_search(input_name, self.thickness, self.contrast_range)
                    elif self.material == 'TMD':
                        ret, img_out = layer_search_TMD(input_name, self.thickness)
                    elif self.material == 'hBN':
                        ret, img_out = layer_search_hbn(input_name)
                    else:
                        print('layer setting error')
                    img_out = self.draw_postition(self.pathDir[self.finished_count], img_out)
                    cv2.imwrite(output_name, img_out)
                    if ret:
                        cv2.imwrite(result_name, img_out)
#                        copyfile(output_name, result_name)
                
#                self.finished_count += 1
                
                
    def draw_postition(self, filename, img_out):
        index = filename[-15:-4]
        size_x = int(index[:2])
        size_y = int(index[3:5])
        pos_x = int(index[6:8])
        pos_y = int(index[9:11])
        
        if size_x == 0 or size_y == 0:
            return img_out
        
        rec_x1 = img_out.shape[1] - 300
        rec_y1 = 100
        rec_x2 = rec_x1 + 200
        rec_y2 = rec_y1 + 200
        
        #print(rec_x1, rec_y1)
        px = rec_x2 - int((rec_x2 - rec_x1)/size_x*pos_x)
        py = rec_y2 - int((rec_y2 - rec_y1)/size_y*pos_y)
        
        
        img_out = cv2.rectangle(img_out,(rec_x1,rec_y1),(rec_x2,rec_y2),(0,255,0),3)
        img_out = cv2.circle(img_out,(px,py), 10, (0,0,255), -1)
        
        return img_out
            
    
    def stop(self):
        pass
    
    
    
class LargeScanThread(QThread):
    large_scan_stop = pyqtSignal(str)
    def __init__(self, camera, thickness = '285nm', magnification = '5x', \
                 material = 'graphene', focus_method = 'Single point', size = '10 mm',
                 contrast_range = [0.028, 0.30]):
        super().__init__()
        self.camera = camera
        self.para = [0, 0, 1, 0]
        self.find_focus_plane_running = True
        self.scan_running = True
        self.thickness = thickness
        self.magnification = magnification
        self.material = material
        self.focus_method = focus_method
        self.size = size
        self.contrast_range = contrast_range
        self.error = False
        self.init_ui()
    
    def init_ui(self):
#        self.stage_focus = Set_Stage_Focus(self.camera)
        self.find_focus_plane = FindFocusPlane(camera = self.camera, 
                                               focus_method = self.focus_method,
                                               size = self.size)
        if self.find_focus_plane.stage.error:
            self.error = True
            return
        self.find_focus_plane.find_focus_plane_stop.connect(self.stop_find_focus_plane)
        self.scan = Scan(self.camera)
        self.scan.scan_stop.connect(self.stop_scan)
        self.layer_search = LayerSearchThread()
        self.current_dir = os.path.abspath(__file__).replace('\\','/')
        self.current_dir = get_folder_from_file(self.current_dir)
        self.xy_step_file = self.current_dir + 'support_file/coordinate_calibration.txt'
        self.x_step = int(np.loadtxt(self.xy_step_file)[0])
        self.y_step = int(np.loadtxt(self.xy_step_file)[1])
#        self.x_step = 14500
#        self.y_step = 14750
        
        
    def run(self):
        if self.error:
            return 
        self.scan.magnification = self.magnification
        self.layer_search.thickness = self.thickness
        self.layer_search.material = self.material
        self.layer_search.filepath = self.scan.save_folder
        self.layer_search.resultpath = get_folder_from_file(self.layer_search.filepath) + '/results'
        self.layer_search.outpath = get_folder_from_file(self.layer_search.filepath) + '/temp'
        self.layer_search.contrast_range = self.contrast_range
        self.layer_search.start()
        self.find_focus_plane.focus_method = self.focus_method
        self.find_focus_plane.size = self.size
        if self.magnification == '20x':
            self.find_focus_plane.autofocus.Fine = True
        for m in range(3):
            for n in range(2):
                self.find_focus_plane.start()
                self.find_focus_plane_running = True
                self.wait_for_find_focus_plane()
                
                self.para = self.find_focus_plane.para
                self.scan.plane_para = self.para
                self.scan_running = True
                start_pos = self.scan.stage.pos
                self.scan.start()
                self.wait_for_scan()
#                print(self.stage_focus.stage.pos, self.scan.stage.pos)
                
#                self.stage_focus.stage.pos = [3800,-11200, 0]
#                self.stage_focus.stage_running = True
#                print('123333333')
#                print(self.stage_focus.stage.pos, self.scan.stage.pos)
                x_temp = self.x_step - (self.scan.stage.pos[0] - start_pos[0])
                y_temp = start_pos[1] - self.scan.stage.pos[1]
                self.scan.stage.move_xyz(x_temp, y_temp, 0)
#                print('456666666')
#                self.stage_focus.wait_stage()
                
            self.find_focus_plane.start()
            self.find_focus_plane_running = True
            self.wait_for_find_focus_plane()
            
            self.para = self.find_focus_plane.para
            self.scan.plane_para = self.para
            self.scan_running = True
            start_pos = self.scan.stage.pos
            self.scan.start()
            self.wait_for_scan()
            if m == 2:
                break
            else:
#                self.stage_focus.stage.pos = [-41200,3800]
#                self.stage_focus.stage_running  =True
                x_temp = start_pos[0] - 2*self.x_step - self.scan.stage.pos[0]
                y_temp = self.y_step - (self.scan.stage.pos[1] - start_pos[1])
                self.scan.stage.move_xyz(x_temp, y_temp, 0)
#                self.stage_focus.wait_stage()


    def stop_find_focus_plane(self, s):
        if s == 'stop':
            #self.stage.terminate()
            self.find_focus_plane_running = False
            
    def stop_scan(self, s):
        if s == 'stop':
            self.scan_running = False
        
    def wait_for_find_focus_plane(self):
        for i in range(2000):
            if not self.find_focus_plane_running:
                print('wait find focus plane finished')
                break
            else:
                time.sleep(0.1)
        if i == 199:
            self.find_focus_plane.terminate()
            self.find_focus_plane_running = False
            print('wait find focus plane time out')
    
    def wait_for_scan(self):
        for i in range(10000):
            if not self.scan_running:
                print('wait scanning finished')
                break
            else:
                time.sleep(0.1)
        if i == 999:
            self.scan.terminate()
            self.scan_running = False
            print('wait scan time out')
            
        
        
            



          
#if __name__=='__main__':
#    app = QApplication(sys.argv)
#    a = LayerSearchThread()
#    a.start()
#    b = a.pathDir
#    sys.exit(app.exec_())

        
    
            
    
    
        
        
        
    
