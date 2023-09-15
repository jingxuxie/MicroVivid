# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 16:45:10 2022

@author: 21255
"""

data=[]            # 读取文件，先解析成十六进制进行保存

local_filename = 'E:/test.txt'

file = open(local_filename, 'rb')
 
while True:           # 可以取得每一个十六进制
    a = file.read(1)      # read（1）表示每次读取一个字节长度的数值
    if not a:
        break
    else:
        if(ord(a)<=15):
            data.append(("0x0"+hex(ord(a))[2:])[2:])  #前面不加“0x0”就会变成eg:7 而不是 07
        else:
            data.append((hex(ord(a)))[2:])  # 最终得到的就是十六进制的字符串表示，便于后续处理
            
            
            

file.close()