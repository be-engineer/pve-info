#coding=utf-8
#通过python脚本获取pve服务器的信息，发送到blynk服务器，然后在手机app上实时显示
import blynklib
#import random
import blynktimer
import platform  #查看系统信息
import psutil  #查看系统相关参数，如温度，内存等
import socket  #获取IP地址
import subprocess  #执行系统命令

#blynk server auth code
BLYNK_AUTH = '4TFvpseX3BYmGhPKZ3bSW3XVpBkLBDDB'

# initialize blynk
#blynk = blynklib.Blynk(BLYNK_AUTH, server='2959w71z50.qicp.vip', port=26514)

#如果你无法实现内网穿透，可以取消下面语句的注释，可以实现本地局域网内的访问
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
update_int = 5  #数据更新间隔，默认为5秒
#message string
WRITE_EVENT_PRINT_MSG = "Write Pin: V{} Value: '{}'"


#连接到服务器时执行
@blynk.handle_event("connect")
def connect_handler():
    for pin in range(20):
        blynk.virtual_sync(pin)
    # 获取本机计算机名称
    hostname = socket.gethostname()
    # 获取本机ip
    ip = socket.gethostbyname(hostname)
    print(WRITE_EVENT_PRINT_MSG.format(0, ip))
    blynk.virtual_write(0, ip)
    #显示os信息到terminal
    os = platform.uname()
    blynk.virtual_write(2, 'OS info')
    blynk.virtual_write(2, '==============')
    for info in os:
        print(WRITE_EVENT_PRINT_MSG.format(2, info))
        blynk.virtual_write(2, info)
    blynk.virtual_write(2, '==============')


#显示terminal command执行结果
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
        info = platform.uname()
        result = '{}\n'.format(info)
    elif values[0] in ALLOWED_COMMANDS_LIST:
        cmd_params = values[0].split(' ')
        try:
            result = subprocess.check_output(cmd_params).decode('utf-8')
            header = '[output]\n'
        except subprocess.CalledProcessError as exe_err:
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
#显示负载使用率
@timer.register(vpin_num=1, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = psutil.getloadavg()
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)


#显示cpu占用率
@timer.register(vpin_num=4, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = psutil.cpu_percent()
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)


#显示内存使用率
#@timer.register(vpin_num=4, interval=8, run_once=False)
@timer.register(vpin_num=update_int, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = psutil.virtual_memory()[2]
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)


'''
#显示硬盘使用率
@timer.register(vpin_num=6, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = psutil.disk_usage('/')[3]
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)


@timer.register(vpin_num=7, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = psutil.disk_usage('/mnt/sdb1')[3]
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)


#显示温度
@timer.register(vpin_num=9, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = psutil.sensors_temperatures()
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)

'''


#显示网路发送数据
@timer.register(vpin_num=11, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    net = psutil.net_io_counters()
    value = '{0:.1f} '.format(net.bytes_recv / 1024 / 1024)
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)


#显示网路接收数据
@timer.register(vpin_num=12, interval=update_int, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    net = psutil.net_io_counters()
    value = '{0:.1f} '.format(net.bytes_sent / 1024 / 1024)
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
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
