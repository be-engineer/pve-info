# !/usr/bin/env python
# -*- coding: utf-8 -*-
#仅作参考用
import psutil
import datetime
import time

# 当前时间
now_time = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
print(now_time)
# 查看cpu的信息
print(u"物理CPU个数: %s" % psutil.cpu_count(logical=False))
cpu = (str)(psutil.cpu_percent(1)) + '%'
print(u"cup使用率: %s" % cpu)
# 查看内存信息,剩余内存.free  总共.total
free = str(round(psutil.virtual_memory().free / (1024.0 * 1024.0 * 1024.0), 2))
total = str(
    round(psutil.virtual_memory().total / (1024.0 * 1024.0 * 1024.0), 2))
memory = int(psutil.virtual_memory().total -
             psutil.virtual_memory().free) / float(
                 psutil.virtual_memory().total)
print(u"物理内存： %s G" % total)
print(u"剩余物理内存： %s G" % free)
print(u"物理内存使用率： %s %%" % int(memory * 100))
# 系统启动时间
print(u"系统启动时间: %s" % datetime.datetime.fromtimestamp(
    psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"))
# 系统用户
users_count = len(psutil.users())
users_list = ",".join([u.name for u in psutil.users()])
print(u"当前有%s个用户，分别是 %s" % (users_count, users_list))
# 网卡，可以得到网卡属性，连接数，当前流量等信息
net = psutil.net_io_counters()
bytes_sent = '{0:.2f} Mb'.format(net.bytes_recv / 1024 / 1024)
bytes_rcvd = '{0:.2f} Mb'.format(net.bytes_sent / 1024 / 1024)
print(u"网卡接收流量 %s 网卡发送流量 %s" % (bytes_rcvd, bytes_sent))
io = psutil.disk_partitions()
del io[-1]
print(
    '-----------------------------磁盘信息---------------------------------------')
print("系统磁盘信息：" + str(io))
for i in io:
    o = psutil.disk_usage(i.device)
    print("总容量：" + str(int(o.total / (1024.0 * 1024.0 * 1024.0))) + "G")
    print("已用容量：" + str(int(o.used / (1024.0 * 1024.0 * 1024.0))) + "G")
    print("可用容量：" + str(int(o.free / (1024.0 * 1024.0 * 1024.0))) + "G")
print('-----------------------------进程信息-------------------------------------')
# 查看系统全部进程
'''
for pnum in psutil.pids():
    p = psutil.Process(pnum)
    print (u"进程名 %-20s  内存利用率 %-18s 进程状态 %-10s 创建时间 %-10s "\
          % (p.name(), p.memory_percent(), p.status(),  p.create_time()))
'''