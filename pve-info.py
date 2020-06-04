#coding=utf-8
#通过python脚本获取服务器的信息，发送到blynk服务器，然后在手机app上实时显示
import blynklib
import random
import blynktimer
import platform #查看系统信息
import psutil  #查看系统相关参数，如温度，内存等
import socket #获取IP地址
import subprocess  #执行系统命令
 
#auth code
BLYNK_AUTH = '4TFvpseX3BYmGhPKZ3bSW3XVpBkLBDDB'

# initialize blynk
#blynk = blynklib.Blynk(BLYNK_AUTH, server='2959w71z50.qicp.vip', port=26514)

#如果你无法实现内网穿透，可以取消下面语句的注释，可以实现本地局域网内的访问
blynk = blynklib.Blynk(BLYNK_AUTH, server='139.155.4.138', port=8080)

# last command in example - just to show error handling
# for certain HW can be added specific commands. 'gpio readall' on PI3b for example
ALLOWED_COMMANDS_LIST = ['ls', 'lsusb', 'ip a', 'lspci','clear','lshw','date','df','pveam list local','pveversion','ls_release -a']
#
READ_PRINT_MSG = "Read Pin: V{}"
# create timers dispatcher instance
timer = blynktimer.Timer() 
 
#message string
WRITE_EVENT_PRINT_MSG = "Write Pin: V{} Value: '{}'"

@blynk.handle_event("connect")
def connect_handler():
    for pin in range(20):
        blynk.virtual_sync(pin)
    # 获取本机计算机名称
    hostname = socket.gethostname()
    # 获取本机ip
    ip = socket.gethostbyname(hostname)
    print(WRITE_EVENT_PRINT_MSG.format(0,hostname+','+ip))
    blynk.virtual_write(0, hostname+','+ip)
    #显示os信息到terminal
    os = platform.uname()
    #info=",".join([m for m in os])
    blynk.virtual_write(2, '系统信息')
    blynk.virtual_write(2, '==============')
    for info in os:
        print(WRITE_EVENT_PRINT_MSG.format(2,info))
        blynk.virtual_write(2, info)
    blynk.virtual_write(2, '==============')
        

#显示terminal command执行结果
@blynk.handle_event('write V2')
def write_handler(pin, values):
    header = ''
    result = ''
    delimiter = '{}\n'.format('=' * 30)
    if values and values[0] in ALLOWED_COMMANDS_LIST:
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
@timer.register(vpin_num=1, interval=5, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value=psutil.getloadavg()
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)
#显示cpu占用率
@timer.register(vpin_num=4, interval=5, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value=psutil.cpu_percent()
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)
#显示内存使用率
#@timer.register(vpin_num=4, interval=8, run_once=False)
@timer.register(vpin_num=5, interval=5, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value=psutil.virtual_memory()[2]
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)
#显示硬盘使用率
@timer.register(vpin_num=6, interval=5, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value=psutil.disk_usage('/')[3]
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)
@timer.register(vpin_num=7, interval=5, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value=psutil.disk_usage('/mnt/sdb1')[3]
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)    
#显示温度    
@timer.register(vpin_num=8, interval=5, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value=psutil.sensors_temperatures()
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
   