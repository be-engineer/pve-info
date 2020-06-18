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


#获取硬盘名称
def get_disk():
    disk = []
    dev_list = os.popen("lsblk -d -o NAME,SIZE,TYPE|grep disk").read().split(
        '\n')
    dev_list = [i for i in dev_list if (len(str(i)) != 0)]
    #result like this
    #['sda    40G disk', 'sdb     5G disk', '']
    for dev in dev_list:
        disk.append('/dev/' + dev[0:3])
    print(disk)  # get each device name like "sda"

    for d in range(len(disk)):
        print('disk%d usage:%.2f%%' % (d, ps.disk_usage(disk[d]).percent))


#获取网络流量和速率
def get_io():
    key_info = ps.net_io_counters(pernic=True).keys()
    recv = {}
    sent = {}
    for key in key_info:
        recv.setdefault(key,
                        ps.net_io_counters(pernic=True).get(key).bytes_recv)
        sent.setdefault(key,
                        ps.net_io_counters(pernic=True).get(key).bytes_sent)

    return key_info, recv, sent


#get all interface total rate
def get_rate(func):
    import time
    key_info, old_recv, old_sent = func()
    time.sleep(1)
    key_info, now_recv, now_sent = func()
    net_in = {}
    net_out = {}
    for key in key_info:
        # float('%.2f' % a)
        net_in.setdefault(
            key,
            float('%.2f' % ((now_recv.get(key) - old_recv.get(key)) / 1024)))
        net_out.setdefault(
            key,
            float('%.2f' % ((now_sent.get(key) - old_sent.get(key)) / 1024)))

    return key_info, net_in, net_out


#main loop
while 1:
    get_disk()
    try:
        key_info, net_in, net_out = get_rate(get_io)

        for key in key_info:
            # lo 是linux的本机回环网卡，以太网是我win10系统的网卡名
            if key != 'lo' or key == '以太网':
                print('%s\nInput:\t %-5sKB/s\nOutput:\t %-5sKB/s\n' %
                      (key, net_in.get(key), net_out.get(key)))
    except KeyboardInterrupt:
        exit()
