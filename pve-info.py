#coding=utf-8
#通过python脚本获取服务器的信息，发送到blynk服务器，然后在手机app上实时显示
import blynklib
import random
import blynktimer
import platform #查看系统信息
import psutil  #查看系统相关参数，如温度，内存等
import socket #获取IP地址
 
#auth code
BLYNK_AUTH = '4TFvpseX3BYmGhPKZ3bSW3XVpBkLBDDB'

# initialize blynk
#blynk = blynklib.Blynk(BLYNK_AUTH, server='2959w71z50.qicp.vip', port=26514)
#如果你无法实现内网穿透，可以取消下面语句的注释，可以实现本地局域网内的访问
blynk = blynklib.Blynk(BLYNK_AUTH, server='139.155.4.138', port=8080)
READ_PRINT_MSG = "Read Pin: V{}"
# create timers dispatcher instance
timer = blynktimer.Timer() 
 
#app connect message
APP_CONNECT_PRINT_MSG = 'App connected'
APP_DISCONNECT_PRINT_MSG = 'App disconnected'

@blynk.handle_event('internal_acon')
def app_connect_handler(*args):
    print(APP_CONNECT_PRINT_MSG)
#when app connected,show host name and ip
    @blynk.handle_event('write V0')
    def write_virtual_pin_handler(pin, value):
        # 获取本机计算机名称
        hostname = socket.gethostname()
        # 获取本机ip
        ip = socket.gethostbyname(hostname)
        print(WRITE_EVENT_PRINT_MSG.format(pin, ip))
    #显示os名称
    @blynk.handle_event('write V1')
    def write_virtual_pin_handler(pin, value):
        os = platform.uname()[0]
        print(WRITE_EVENT_PRINT_MSG.format(pin,os ))
    #显示hostname
    @blynk.handle_event('write V2')
    def write_virtual_pin_handler(pin, value):
        host = platform.uname()[1]
        print(WRITE_EVENT_PRINT_MSG.format(pin,host))
    #显示os版本
    @blynk.handle_event('write V3')
    def write_virtual_pin_handler(pin, value):
        rev = platform.uname()[2]
        print(WRITE_EVENT_PRINT_MSG.format(pin,rev))


@blynk.handle_event('internal_adis')
def app_disconnect_handler(*args):
    print(APP_DISCONNECT_PRINT_MSG)

WRITE_EVENT_PRINT_MSG = "Write Pin: V{} Value: '{}'"


#显示cpu负载率
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
#显示温度    


#run loop
while True:
    blynk.run()
    timer.run()