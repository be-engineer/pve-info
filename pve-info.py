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

# blynk server auth code
BLYNK_AUTH = '4TFvpseX3BYmGhPKZ3bSW3XVpBkLBDDB'

# initialize blynk
# blynk = blynklib.Blynk(BLYNK_AUTH, server='2959w71z50.qicp.vip', port=26514)

# 如果你无法实现内网穿透，可以取消下面语句的注释，可以实现本地局域网内的访问
blynk = blynklib.Blynk(BLYNK_AUTH, server='139.155.4.138', port=8080)

# last command in example - just to show error handling
# for certain HW can be added specific commands. 'gpio readall' on PI3b for example
ALLOWED_COMMANDS_LIST = [
    'lsusb', 'ip a', 'lspci', 'lshw', 'date', 'df', 'pveversion', 'help',
    'free', 'pveam', 'networkctl', 'ls', 'lsb_release', 'cat', 'osinfo'
]
#
READ_PRINT_MSG = "Read Pin: V{}"
# create timers dispatcher instance
timer = blynktimer.Timer()
update_int = 5  # 数据更新间隔，默认为5秒
# message string
WRITE_EVENT_PRINT_MSG = "Write Pin: {} Value: '{}'"


# 连接到服务器时执行
@blynk.handle_event("connect")
def connect_handler():
    for pin in range(20):
        blynk.virtual_sync(pin)
    # 获取本机计算机名称
    hostname = socket.gethostname()
    # 获取本机ip
    ip = socket.gethostbyname(hostname)
    print(WRITE_EVENT_PRINT_MSG.format('IP', ip))
    blynk.virtual_write(0, ip)
    # 显示os信息到terminal
    os = pl.uname()
    blynk.virtual_write(2, 'OS info')
    blynk.virtual_write(2, '==============')
    for info in os:
        print(WRITE_EVENT_PRINT_MSG.format('OS', info))
        blynk.virtual_write(2, info)
    blynk.virtual_write(2, '==============')


# 显示terminal command执行结果
@blynk.handle_event('write V2')
def write_handler(pin, values):
    header = ''
    result = ''
    delimiter = '{}\n'.format('=' * 30)
    if values[0] == 'help':
        header = '[Allowed commands]\n'
        result = '{}\n'.format('\n'.join(ALLOWED_COMMANDS_LIST))
    elif values[0] == 'osinfo':
        header = '[output]\n'
        info = pl.uname()
        result = '{}\n'.format('\n'.join(info))
    elif values[0] in ALLOWED_COMMANDS_LIST:
        cmd_params = values[0].split(' ')
        try:
            result = sub.check_output(cmd_params).decode('utf-8')
            header = '[output]\n'
        except sub.CalledProcessError as exe_err:
            header = '[error]\n'
            result = 'Return Code: {}\n'.format(exe_err.returncode)
        except Exception as g_err:
            print("Command caused '{}'".format(g_err))
    else:
        header = '[Allowed commands]\n'
        result = '{}\n'.format('\n'.join(ALLOWED_COMMANDS_LIST))

    # communicate with terminal if help or some allowed command
    if result:
        output = '{}{}{}{}'.format(header, delimiter, result, delimiter)
        print(output)
        blynk.virtual_write(pin, output)
        blynk.virtual_write(pin, '\n')


#
# 显示负载使用率
@timer.register(vpin_num=1, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = ps.getloadavg()
    print(WRITE_EVENT_PRINT_MSG.format('Load', value))
    blynk.virtual_write(vpin_num, value)


# 显示cpu占用率
@timer.register(vpin_num=3, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = ps.cpu_percent()
    print(WRITE_EVENT_PRINT_MSG.format('CPU', value))
    blynk.virtual_write(vpin_num, value)


# 显示内存使用率
# @timer.register(vpin_num=4, interval=8, run_once=False)
@timer.register(vpin_num=4, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = ps.virtual_memory()[2]
    print(WRITE_EVENT_PRINT_MSG.format('Mem', value))
    blynk.virtual_write(vpin_num, value)

# 显示系统硬盘大小
@timer.register(vpin_num=5, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    # 读取系统硬盘使用率
    re = format(float(sub.check_output(
        ["fdisk", "-s", "/dev/sdb"]))/1024/1024, '.2f')
    value = format(float(re), ',')
    print(WRITE_EVENT_PRINT_MSG.format('Disk1', value))
    blynk.virtual_write(vpin_num, value)

# 显示USB硬盘大小
@timer.register(vpin_num=6, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    # 读取系统硬盘使用率,GB
    re = format(float(sub.check_output(
        ["fdisk", "-s", "/dev/sda"]))/1024/1024, '.2f')
    value = format(float(re), ',')
    print(WRITE_EVENT_PRINT_MSG.format('Disk2', value))
    blynk.virtual_write(vpin_num, value)

# 显示硬盘使用率
@timer.register(vpin_num=7, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    # 读取系统硬盘使用率
    value = ps.disk_usage('/')[3]
    print(WRITE_EVENT_PRINT_MSG.format('Disk1%', value))
    blynk.virtual_write(vpin_num, value)


@timer.register(vpin_num=8, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    # 读取第二块硬盘使用率
    value = ps.disk_usage(ps.disk_partitions()[2][1])[3]
    print(WRITE_EVENT_PRINT_MSG.format('Disk2%', value))
    blynk.virtual_write(vpin_num, value)


# 显示温度
# ps.sensors_temperatures()输出结果
# {'acpitz': [shwtemp(label='', current=27.8, high=105.0, critical=105.0), shwtemp(label='', current=29.8, high=105.0, critical=105.0)], 'coretemp': [shwtemp(label='Package id 0', current=49.0, high=100.0, critical=100.0), shwtemp(label='Core 0', current=49.0, high=100.0, critical=100.0), shwtemp(label='Core 1', current=45.0, high=100.0, critical=100.0), shwtemp(label='Package id 0', current=49.0, high=100.0, critical=100.0), shwtemp(label='Core 0', current=49.0, high=100.0, critical=100.0), shwtemp(label='Core 1', current=45.0, high=100.0, critical=100.0)]}

# cpu 1温度
@timer.register(vpin_num=9, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = ps.sensors_temperatures().items()[1][1][2][1]
    print(WRITE_EVENT_PRINT_MSG.format('tCPU1', value))
    blynk.virtual_write(vpin_num, value)

# cpu 2
@timer.register(vpin_num=10, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = ps.sensors_temperatures().items()[1][1][3][1]
    print(WRITE_EVENT_PRINT_MSG.format('tCPU2', value))
    blynk.virtual_write(vpin_num, value)

# 主板温度
@timer.register(vpin_num=11, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    # ps.sensors_temperatures().items()[0][1][0][1] 或ps.sensors_temperatures().items()[0][1][1][1]
    value = ps.sensors_temperatures().items()[0][1][1][1]
    print(WRITE_EVENT_PRINT_MSG.format('tBoard', value))
    blynk.virtual_write(vpin_num, value)

# 硬盘温度
@timer.register(vpin_num=12, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    # result '/dev/sdb: Kston 64GB: 36\xc2\xb0C\n'
    re = sub.check_output(['hddtemp', '/dev/sdb'])
    value = re[-7:-4]
    print(WRITE_EVENT_PRINT_MSG.format('tHDD1', value))
    blynk.virtual_write(vpin_num, value)

# 显示网路发送数据
@timer.register(vpin_num=15, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    # net='{0:.2f} '.format(net / 1024 / 1024 / 1024)
    value = format(ps.net_io_counters()[0] / 1024 / 1024 / 1024, '.3f')  # TB
    #value = format(float(net), ',')
    print(WRITE_EVENT_PRINT_MSG.format('Sent', value))
    blynk.virtual_write(vpin_num, value)


# 显示网路接收数据
@timer.register(vpin_num=16, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = format(ps.net_io_counters()[1] / 1024 / 1024/1024, '.3f')  # TB
    #value = format(float(net), ',')
    print(WRITE_EVENT_PRINT_MSG.format('Rec', value))
    blynk.virtual_write(vpin_num, value)


###########################################################
# infinite loop that waits for event
###########################################################
try:
    while True:
        blynk.run()
        timer.run()
except KeyboardInterrupt:
    blynk.disconnect()
