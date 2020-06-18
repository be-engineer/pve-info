# coding=utf-8
# 通过python脚本获取pve服务器的信息，发送到blynk服务器，然后在手机app上实时显示
# python2.7
import blynklib
# import random
import blynktimer
import platform as pl  # 查看系统信息
import psutil as ps  # 查看系统相关参数，如温度，内存等
import socket  # 获取IP地址
import subprocess as sub  # 执行系统命令
import time
import os

disk = []
dev_list = os.popen("lsblk -d -o NAME,SIZE,TYPE|grep disk").read().split('\n')
dev_list = [i for i in dev_list if (len(str(i)) != 0)]
#result like this
#['sda    40G disk', 'sdb     5G disk', '']
for dev in dev_list:
    disk.append('/dev/' + dev[0:3])
print(disk)  # get each device name like "sda"

for d in range(len(disk)):
    print('disk%d usage:%.2f%%' % (d, ps.disk_usage(disk[d]).percent))
