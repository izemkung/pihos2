import RPi.GPIO as GPIO ## Import GPIO library
import ConfigParser
import os
import time
import requests

def SendAlartFun(channel):
    try:
        resp = requests.get(nti_url+'?ambulance_id={0}'.format(id), timeout=2.001)
        print ('content     ' + resp.content) 
    except:
        print 'SendAlartFun Connection lost'
        
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

while True:
    if(GPIO.input(4) == 0):
        print('Power Off')
        time.sleep(10)
        os.system('sudo shutdown -h now')
        break
GPIO.cleanup()