import RPi.GPIO as GPIO ## Import GPIO library
import ConfigParser
import os
import time
import requests
import sys
import socket
import serial
import fcntl
import struct

REMOTE_SERVER = "www.google.com"


def internet_on():
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(REMOTE_SERVER)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def SendAlartFun(channel):
    try:
        
        resp = requests.get(nti_url+'?ambulance_id={0}'.format(id), timeout=2.001)
        print ('content     ' + resp.content) 
    except:
        print 'SendAlartFun Connection lost'

def SendStatusFun(message):
    try:
        print id
        ip = get_ip_address('ppp0') 
        print ip
        print SID
        print IMEI
        api = nti_url.split("/")
        print api[2]
        resp = requests.get('http://188.166.197.107:8001?id={0}&ip={1}&sid={2}&imei={3}&api={4}&msg={5}'.format(id,ip,SID,IMEI,api[2],message), timeout=2.001)
        print ('content     ' + resp.content) 
        return True
    except:
        print 'SendStatusFun Connection lost'
    return False

def GetSIDFun(message):
    try:
        ser.flushInput()
        ser.flushOutput()
        time.sleep(2)
        ser.write('AT+QCCID\r')
        time.sleep(2)

        for num in range(0, 10):
            bufsid = ser.readline()
            if(len(bufsid) > 20):
                break

        replacements = (',', '\r', '\n', '?')
        for r in replacements:
            bufsid = bufsid.replace(r, ' ')
        CID = bufsid.split(" ")
        SID = CID[1]
        
        ser.write('AT+GSN\r')
        time.sleep(1)
        for num in range(0, 10):
            bufemi = ser.readline()
            if(len(bufemi) > 10):
                break

        replacements = (',', '\r', '\n', '?')
        for r in replacements:
            bufemi = bufemi.replace(r, ' ')
        emi = bufemi.split(" ")
        print emi
        IMEI = emi[0]
        print SID
        print len(SID)
        print IMEI
        print len(IMEI)
    except:
        print SID
        print IMEI
        print 'Get SID Error'
        
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

if os.path.exists("/home/pi/usb/config.ini") == False:
    print("config.ini error")
    os.system('sudo mount /dev/sda1 /home/pi/usb/')
    exit()


#if os.path.exists("/home/pi/usb/pic") == True:
#    print("Delete Pic Foder!!!")
    #os.system('sudo mount /dev/sda1 /mnt/usbdrive')
#    os.system('sudo rm -rf /home/pi/usb/pic')
#    os.system('sudo mkdir /home/pi/usb/pic')
 #   os.system('sudo mkdir /home/pi/usb/pic/ch0')
#    os.system('sudo mkdir /home/pi/usb/pic/ch1')

#if os.path.exists("/home/pi/usb/vdo") == True:
 #   print("Delete Vdo Foder!!!")
    #os.system('sudo mount /dev/sda1 /mnt/usbdrive')
 #  os.system('sudo rm -rf /home/pi/usb/vdo')
  #  os.system('sudo mkdir /home/pi/usb/vdo')
 #   os.system('sudo mkdir /home/pi/usb/vdo/ch0')
  #  os.system('sudo mkdir /home/pi/usb/vdo/ch1')
    
       
Config = ConfigParser.ConfigParser()
Config.read('/home/pi/usb/config.ini')

id =  ConfigSectionMap('Profile')['id']
timevdo = ConfigSectionMap('Profile')['timevdo']
timepic = ConfigSectionMap('Profile')['timepic']
nti_url = ConfigSectionMap('Profile')['nti_api']

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) ## Use board pin numbering
GPIO.setup(3, GPIO.IN) # Alaet
GPIO.setup(4, GPIO.IN) # Power

GPIO.add_event_detect(3, GPIO.RISING, callback=SendAlartFun, bouncetime=100)

sendStart = False

time.sleep(2)
ser = serial.Serial('/dev/ttyUSB2', 115200, timeout=.5)
ser.write('AT+QGPS=1\r')
ser.write('AT+QGPS=1\r')
ser.write('ATE0\r')
ser.write('ATE0\r')
time.sleep(2)

SID = "null"
IMEI = "null"

while True:
    if(sendStart == False) :
        if(internet_on() == True ) and (len(SID) > 13):  
            if(SendStatusFun('Power On') == True):
                sendStart = True
    if(len(SID) < 13):
        GetSIDFun('msg')  

    if(GPIO.input(4) == 0):
        print('Power Off')
        SendStatusFun('Power Off')
        time.sleep(10)
        
        os.system('sudo shutdown -h now')
        break
GPIO.cleanup()