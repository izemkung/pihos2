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
import subprocess

REMOTE_SERVER = "www.google.com"
flagDetectHW_GPS = False
VERSION_FW = 34
version_config = "34"
IMEI_CONFIG = ""
CAM_COUNT = ""
serModem = ""

def checkCamera():
    global CAM_COUNT
    out = ''
    try:
        byteOutput = subprocess.check_output(['lsusb'])
        out = byteOutput.decode('UTF-8').rstrip()
        #print(out)
        CAM_COUNT = "_C"
        CAM_COUNT += str(out.count('Webcam'))
        CAM_COUNT += ":"
        CAM_COUNT += str(out.count('Logitech'))
        #print(CAM_COUNT)

    except subprocess.CalledProcessError as e:
        print("Error lsusb", e.output)
        return "error"
    


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
        resp = requests.get(nti_url+'?ambulance_id={0}'.format(id), timeout=3.001)
        print ('content     ' + resp.content) 
    except:
        print 'SendAlartFun Connection lost'

def SendStatusFun(message):
    global IMEI_CONFIG
    global CAM_COUNT
    global serModem
    #try:
    serModem.flushInput()
    serModem.flushOutput()
    time.sleep(0.1)
    serModem.write('AT+QCCID\r')
    time.sleep(2)

    for num in range(0, 10):
        bufsid = serModem.readline()
        if len(bufsid) >= 20 :
            break

    replacements = (',', '\r', '\n', '?')
    for r in replacements:
        bufsid = bufsid.replace(r, ' ')
    SID = bufsid.split(" ")

    if(len(SID) > 1):
        if len(SID[1]) <= 13:
            SID[1] = "On_LAN"
    else:
        SID = ["","On_LAN"]

    sidOk = True
        #return False

    #print SID
    #SID = CID[1]
    
    serModem.write('AT+GSN\r')
    time.sleep(1)
    for num in range(0, 10):
        bufemi = serModem.readline()
        if len(bufemi) >= 10 :
            break

    replacements = (',', '\r', '\n', '?')
    for r in replacements:
        bufemi = bufemi.replace(r, ' ')
    IMEI = bufemi.split(" ")
    IMEI_CONFIG = IMEI
    #print IMEI
    #IMEI = emi[0]
    
    
    #print id
    try:
        ip = get_ip_address('ppp0') 
    except:
        ip = "On_LAN"
    #print ip
    #print SID
    #print IMEI
    api = "27.254.149.188"
    #print api[2]

    

    if flagDetectHW_GPS == True:
        api += '_HW_Sv3.2_'
    else:
        api += '_UC_Sv3.2_'

    api += version_config

    checkCamera()
    api += CAM_COUNT
    print ('http://188.166.197.107:8001?id={0}&ip={1}&sid={2}&imei={3}&api={4}&msg={5}'.format(id,ip,SID[1],IMEI[0],api,message))
    resp = requests.get('http://188.166.197.107:8001?id={0}&ip={1}&sid={2}&imei={3}&api={4}&msg={5}'.format(id,ip,SID[1],IMEI[0],api,message), timeout=3.001)
    
    print ('content     ' + resp.content) 
    return True
    #except:
        #print 'SendStatusFun Connection lost'
    return False

def SetDeviceGPSisHW(section):
    try:
        if section == True:
            print "gpsd > GPS HW"
            os.system('sudo gpsd {0} -F /var/run/gpsd.sock'.format(GPSPortHW))
        else:
            print "gpsd > GPS UC20"
            port = FindGPS_SerialModem()
            if(port == 'error'):
                port = GPSPortUC20
            os.system('sudo gpsd {0} -F /var/run/gpsd.sock'.format(port))
        
        time.sleep(1)
        os.system('sudo systemctl restart gpsd.socket')
        #os.system('sudo systemctl start gpsd.socket')

        #os.system('sudo systemctl enable gpsd.socket')
        #os.system('sudo systemctl start gpsd.socket')
    except :
        print "Init gpsd Error"
        
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

def FindSerialModem():
    _port = 'Error'
    for num in range(0, 4):
        _port = '/dev/ttyUSB{0}'.format(num)
        try:
            ser = serial.Serial(_port,115200, timeout=1.0 , rtscts=True, dsrdtr=True)
            ser.flushInput()
            ser.flushOutput()
            time.sleep(1)
            ser.write('AT\r')
            ser.write('AT\r')
            for num in range(0, 4):
                _bufin = ser.readline()
                print('Checking {0} Data In {1}'.format(_port,_bufin))
                if _bufin.count('OK'):
                    print('Found!! {0} OK!!'.format(_port))
                    ser.close()
                    time.sleep(1)
                    return _port
            ser.close()
            time.sleep(1)
        except:
            print('Port {0} busy'.format(_port))

    return _port

def FindGPS_SerialModem():
    _port = 'Error'
    for num in range(0, 4):
        _port = '/dev/ttyUSB{0}'.format(num)
        try:
            ser = serial.Serial(_port,115200, timeout=1.0 , rtscts=True, dsrdtr=True)
            for num in range(0, 4):
                _bufin = ser.readline()
                print('Checking {0} Data In {1}'.format(_port,_bufin))
                if _bufin.count('$'):
                    print('Found!! {0} GPS!!'.format(_port))
                    ser.close()
                    time.sleep(1)
                    return _port
            ser.close()
            time.sleep(1)
        except:
            print('Port {0} busy'.format(_port))

    return _port

print "Start GPIO"


#=========================GET IMEI UC20 
time.sleep(5)
try:
    port = FindSerialModem()
    if(port == 'Error'):
        port = '/dev/ttyUSB2'

    serModem = serial.Serial(port, 115200, timeout=1.0 , rtscts=True, dsrdtr=True)
    
    serModem.write('AT+GSN\r')
    for num in range(0, 5):
        serModem.write('AT+GSN\r')
        bufemi = serModem.readline()
        if len(bufemi) >= 15 :
            break
    replacements = (',', '\r', '\n', '?')
    for r in replacements:
        bufemi = bufemi.replace(r, ' ')
    IMEI = bufemi.split(" ")
    print IMEI[0]
    IMEI_CONFIG = IMEI
    time.sleep(1)
    serModem.write('AT+QGPS=1\r')
    serModem.write('ATE0\r')
    

except:
    print "Get IMEI from Serial ttyUSB2 Error"
    time.sleep(10)
    exit()
    #os.system('sudo reboot')
time.sleep(1)

#=========================Detect HW GPS
GPSPortUC20 = '/dev/ttyUSB1'
GPSPortHW =  '/dev/ttyAMA0'

try:
  os.system('sudo chmod +x /home/pi/pihos/connect.sh')
  os.system('sudo timedatectl set-ntp True')
  
  os.system('sudo systemctl enable gpsd.socket')
  os.system('sudo systemctl start gpsd.socket')
  
  #os.system('sudo systemctl stop gpsd.socket')
  #os.system('sudo systemctl disable gpsd.socket')

  #os.system('sudo systemctl stop gpsd.socket')
  #os.system('sudo systemctl disable gpsd.socket')
except :
  print "Stop gpsd Error"

time.sleep(5)
#==============================HW Serial GPS Detection==============================
try:
    serDetec = serial.Serial(GPSPortHW, 9600 , timeout=1.0 , rtscts=True, dsrdtr=True)
    serDetec.flushInput()
    serDetec.flushOutput()
    time.sleep(1)
    for num in range(0, 20):
        #time.sleep(0.5)
        bufemi = serDetec.readline()
        print bufemi
        if bufemi[0] == '$' and bufemi[1] == 'G':
            flagDetectHW_GPS = True
            print "===========HW GPS Detect==========="
            break
    serDetec.close()
except:
    print "Open Serial HW Error"
    #time.sleep(10)
    #os.system('sudo reboot')


SetDeviceGPSisHW(flagDetectHW_GPS)

#sudo gpsd /dev/ttyUSB1 -F /var/run/gpsd.sock
#input2 = 0
#for num in range(0, 4):
#    port = '/dev/ttyUSB{0}'.format(num)
#    try:
#        ser = serial.Serial(port, 115200, timeout=.5)
#        input = ser.inWaiting()
#        print('Checking {0} Data In {1}'.format(port,input))
#        time.sleep(5)
#        input = ser.inWaiting()
#    except:
#        print('Port {0} busy'.format(port))

#    try:
#        input2 = 0
#        for count in range(0, 10):
#            inputS = ser.readline()
#            input2 += len(inputS)
#            print(inputS)
#        ser.close()
#    except:
#        print('Port {0} Except'.format(port))
#    print('Checked {0} Data In {1} DataS {2}'.format(port,input,input2))
#    if(input > 200) or (input2 > 100):
#        print('{0} Ok!!!'.format(port))
#        GPSPortUC20 = port
#        break
#time.sleep(10)
#os.system('clear') #clear the terminal (optional)

def UpdateConfigs():
    global IMEI_CONFIG
    global id
    global version_config
    print IMEI_CONFIG
    print 'http://159.89.208.90:5001/config/' + IMEI_CONFIG[0] 
    #+ '?ambulance_id=' + id + '&version=' + version_config
    try:
        resp = requests.get('http://159.89.208.90:5001/config/' + IMEI_CONFIG[0])
        #+ '?ambulance_id=' + id + '&version=' + version_config)
        #resp = requests.get('http://188.166.197.107/Config_API.php?IMEI=861075028784957')
        configJSON = resp.json()
        print configJSON
    except :
        print "Get config error"
        return

    f = open('/home/pi/_config.ini', "w")
    f.write("[Profile]")
    f.write("\nconfig: "+ str(configJSON['config']))
    f.write("\nid: "+ str(configJSON['id']))
    f.write("\ntimevdo: "+ str(configJSON['timevdo']))
    f.write("\ntimepic: "+ str(configJSON['timepic']))
    f.write("\ngps_api: "+ configJSON['gps_api'])
    f.write("\npic_api: "+ configJSON['pic_api'])
    f.write("\nnti_api: "+ configJSON['nti_api'])
    f.write("\ngps_uc20: "+ configJSON['gps_uc20'])
    f.write("\nsound: "+ configJSON['sound'])
    f.write("\nversion: "+ str(configJSON['version']))
    f.write("\nover_speed: "+ str(configJSON['over_speed']))
    f.write("\nkey0: "+ configJSON['key0'])
    f.write("\nkey1: "+ configJSON['key1'])
    f.write("\nrest: "+ configJSON['rest'])
    f.write("\n[Value]")
    f.write("\nenable : 0")
    f.write("\ndisable : 0")

    f.close()

#{u'VERSION': u'72b1d9e5ef932f91e17b603f0cc0492cafa4a5db', u'TIME_PIC': u'0', u'CRASH_GAIN': u'10', u'REPO': u'pihos2', u'NUM': u'1',
# u'API_PIC': u'http://safetyam.tely360.com/api/upload.php', u'TIME_GPS': u'1', u'IMEI': u'861075028784957',  
# u'API_NTI': u'http://safetyam.tely360.com/api/notification.php', u'ID': u'99', u'API_GPS': u'http://safetyam.tely360.com/api/tracking.php', u'TIME_VDO': u'10'}
#id: 99
#timevdo: 10
#timepic: 1
#gps_api: http://safetyam.tely360.com/api/tracking.php
#pic_api: http://safetyam.tely360.com/api/upload.php
#nti_api: http://safetyam.tely360.com/api/notification.php

#if os.path.exists("config.ini") == False  :
#print("local config.ini error")
#print("load config.ini")
#if internet_on() == True :
#    resp = requests.get('http://188.166.197.107/Config_API.php?IMEI={0}'.format(IMEI[0]))
#    if os.path.exists("config.ini") == False  :
#        os.system('sudo touch /home/pi/config.ini')
#    with open("/home/pi/config.ini", "r+") as f:
#        f.seek(0) # rewind
#        f.write("[Profile]")
#        f.write("\r\nid : " + resp.json()['ID'])
#        f.write("\r\ntimevdo : " + resp.json()['TIME_VDO'])
#        f.write("\r\ntimepic : " + resp.json()['TIME_PIC'])
#        f.write("\r\ngps_api : " + resp.json()['API_GPS'])
#        f.write("\r\nnti_api : " + resp.json()['API_NTI'])
#        f.write("\r\pic_api : " + resp.json()['API_PIC'])
#        f.close()
#else: 
    #print("load config.ini internet Error")
'''       
if os.path.exists("/home/pi/usb/config.ini") == False:
    print("usb config.ini error")
    os.system('sudo mount /dev/sda1 /home/pi/usb/')
    exit()
else:
    if os.path.exists("/home/pi/config.ini") == True:
        os.system('sudo rm -rf config.ini')
    os.system('sudo mv /home/pi/usb/config.ini /home/pi/config.ini')
'''
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

print "Wait Internet.."  
while (internet_on() == False):
    time.sleep(20)
print "Internet..OK!!!"  

checkCamera()
UpdateConfigs()

try:      
    Config = ConfigParser.ConfigParser()
    Config.read('/home/pi/_config.ini')
    id =  ConfigSectionMap('Profile')['id']
    print id
except:
    print "Read config ERROR"  
    #Config.read('/home/pi/usb/config.ini')  

id =  ConfigSectionMap('Profile')['id']
print id 
timevdo = ConfigSectionMap('Profile')['timevdo']
print timevdo
timepic = ConfigSectionMap('Profile')['timepic']
print timepic
nti_url = ConfigSectionMap('Profile')['nti_api']
print nti_url
try:
  version_config = ConfigSectionMap('Profile')['version']
except:
  version_config = "35"
  print("exception version")
print  'version > ',version_config

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) ## Use board pin numbering
GPIO.setup(3, GPIO.IN) # Alaet
GPIO.setup(4, GPIO.IN) # Power

GPIO.add_event_detect(3, GPIO.RISING, callback=SendAlartFun, bouncetime=100)

sendStart = False

current_time = time.time()
timeout2 = time.time()
timeStart = time.time()
timeout = time.time() + 60
while True:
    time.sleep(2)
    current_time = time.time()
#I/O Power on
    if sendStart == False  :
        if internet_on() == True :  
            if(SendStatusFun('Power Start') == True):
                sendStart = True
                UpdateConfigs()
                print sendStart

#I/O Power off
    if(GPIO.input(4) == 0):
        print('Power Off')
        SendStatusFun('Power Off {0:.1f} Min'.format((current_time - timeStart)/60))
        time.sleep(20)
        os.system('sudo shutdown -h now')
        break

#On line status
    if time.time() > timeout2:
        print "Sent Online Status" 
        SendStatusFun('On {0:.1f} Min'.format((current_time - timeStart)/60))
        timeout2 = time.time() + 600

#Ennable GPS
    if time.time() > timeout:
        timeout = time.time() + 60
        serModem.write('ATE0\r')
        serModem.write('AT+QGPS=1\r')
        for num in range(0, 5):
            bufemi = serModem.readline()
        print "Set Starting GPS"  

serModem.close()
GPIO.cleanup()