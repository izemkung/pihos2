from time import gmtime, strftime
import RPi.GPIO as GPIO ## Import GPIO library
import time
import datetime
import imutils
import numpy as np
import cv2
import argparse
import os
import glob
import cv2
import cv
import base64
import requests
import urllib2
import httplib
import threading

import ConfigParser
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

if os.path.exists("/home/pi/config.ini") == False:
    print("config.ini error")
    #os.system('sudo mount /dev/sda1 /home/pi/usb')
    exit()
    
Config = ConfigParser.ConfigParser()
Config.read('/home/pi/config.ini')

id =  ConfigSectionMap('Profile')['id']
timevdo = ConfigSectionMap('Profile')['timevdo']
timepic = ConfigSectionMap('Profile')['timepic']
gps_url = ConfigSectionMap('Profile')['gps_api']
pic_url = ConfigSectionMap('Profile')['pic_api']

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="/home/pi/usb/",
	help="path to output")
ap.add_argument("-i", "--idcamera", type=int, default=0,
	help="camera should be used")
ap.add_argument("-t", "--timevdo", type=int, default=10,
	help="time of output video(min)")
ap.add_argument("-c", "--timepic", type=float, default=0.9,# 0.95
	help="save pic evev sec(sec)")
args = vars(ap.parse_args())

floderOk = 0

if os.path.exists("/home/pi/usb/vdo") == False:
    os.system('sudo mkdir /home/pi/usb/vdo')
else:
    floderOk += 1

if os.path.exists("/home/pi/usb/vdo/ch0") == False:
    os.system('sudo mkdir /home/pi/usb/vdo/ch0')
else:
    floderOk += 1

if os.path.exists("/home/pi/usb/vdo/ch1") == False:
    os.system('sudo mkdir /home/pi/usb/vdo/ch1')
else:
    floderOk += 1

if os.path.exists("/home/pi/usb/pic") == False:
    os.system('sudo mkdir /home/pi/usb/pic')
else:
    floderOk += 1

if os.path.exists("/home/pi/usb/pic/ch0") == False:
    os.system('sudo mkdir /home/pi/usb/pic/ch0')
else:
    floderOk += 1

if os.path.exists("/home/pi/usb/pic/ch1") == False:
    os.system('sudo mkdir /home/pi/usb/pic/ch1')
else:
    floderOk += 1

print floderOk

flagUSBOk = False

if floderOk == 6:
    flagUSBOk = True
else:
    flagUSBOk = False

os.environ['TZ'] = 'Asia/Bangkok'
time.tzset()

print("Camera "+str(args["idcamera"])) 

    
cap0 = cv2.VideoCapture(0)
cap1 = cv2.VideoCapture(1)

#set the width and height, and UNSUCCESSFULLY set the exposure time
#Config 
timeSavePic = args["timepic"]
timeVDO = args["timevdo"]

cap0.set(3,1360/2)
cap0.set(4,768/2)
cap0.set(5,20)

cap1.set(3,1360/2)
cap1.set(4,768/2)
cap1.set(5,20)

#cap.set(3,1024)
#cap.set(4,768)
picResolotion = 2
#time.sleep(2)

#cap.set(15, -8.0)
#cap.set(15, 0.1)

# Define the codec and create VideoWriter object
fourcc = cv2.cv.CV_FOURCC('D','I','V','X')

ret, frame = cap0.read()
(h, w) = frame.shape[:2]
print("Vdo:"+str(w)+"x"+str(h) + " Pic:"+str(w/picResolotion)+"x"+str(h/picResolotion) )

vdoname = gmtime()

if(flagUSBOk == True):
    out0 = cv2.VideoWriter(args["output"]+ 'vdo/ch0'+'/vdo_{}.avi'.format(strftime("%d%m%Y%H%M%S", vdoname)),fourcc, 20.0, (w,h))
    out1 = cv2.VideoWriter(args["output"]+ 'vdo/ch1'+'/vdo_{}.avi'.format(strftime("%d%m%Y%H%M%S", vdoname)),fourcc, 20.0, (w,h))
    print(args["output"]+ 'vdo/ch' +str(args["idcamera"]) +'/vdo_{}.avi'.format(strftime("%d%m%Y%H%M%S", vdoname))) 

#Picture 
current_time = 0
last_time = 0

countPic = 0
endtime = 0
framePic = None 
startTime = time.time()

font = cv2.FONT_HERSHEY_SIMPLEX

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) ## Use board pin numbering
GPIO.setup(4, GPIO.IN) # Power
GPIO.setup(17,GPIO.OUT)

KillPs = False
jpg_as_text0 = None
jpg_as_text1 = None
flagPic = False

def myThreadSend ():
    global jpg_as_text0
    global jpg_as_text1
    global flagPic
    global KillPs
    current_time_T = 0
    last_time_T = 0
    countPic_T = 0
    connectionError = 0
    while(GPIO.input(4) == 0):
        print("Ok!!!")
        time.sleep(0.2)
        GPIO.output(17,True)
        time.sleep(0.2)
        GPIO.output(17,False)
    while (KillPs == False): 
        current_time_T = time.time() * 1000
        if flagPic == True:
            if current_time_T - last_time_T > 1000:
                flagPic = False
                last_time_T = current_time_T
                data = {'ambulance_id':id,'images_name_1':jpg_as_text0,'images_name_2':jpg_as_text1}
                try:
                    r = requests.post(pic_url, data=data)
                    print r
                    connectionError = 0
                    GPIO.output(17,True)
                    countPic_T += 1
                    print("Send > "+str(countPic_T)) 
                    print("FreamRate > "+str(1000/(current_time_T - last_time_T))+" Hz")
                    
                except:
                    connectionError += 1
                    if connectionError > 10:
                        connectionError = 0
                        print "Connection Error"
    print("Time > "+str(timeVDO) + " m NumPic > "+str(countPic_T)) 


while(GPIO.input(4) == 0):
    print("Ok!!!")
    time.sleep(0.2)
    GPIO.output(17,True)
    time.sleep(0.2)
    GPIO.output(17,False)

t1 = threading.Thread(target=myThreadSend)
t1.start()

while(cap0.isOpened() and cap1.isOpened()):
    GPIO.output(17,False)
    current_time = time.time() * 1000
 
    ret0, frame0 = cap0.read()
    ret1, frame1 = cap1.read()
    if ret0 == True and ret1 == True:
        if current_time - endtime > 10:
            framePic0 = imutils.resize(frame0, w/picResolotion)
            framePic1 = imutils.resize(frame1, w/picResolotion)
            cv2.putText(framePic0,"Ambulance "+ str(id) + " id 0"+" {}".format(strftime("%d %b %Y %H:%M:%S")) ,(2,(h/picResolotion) - 5), font, 0.3,(0,255,255),1)    
            cv2.putText(framePic1,"Ambulance "+ str(id) + " id 1"+" {}".format(strftime("%d %b %Y %H:%M:%S")) ,(2,(h/picResolotion) - 5), font, 0.3,(0,255,255),1)    
            
            
            #cv2.imwrite(args["output"]+  'pic/ch' +str(args["idcamera"])  +'/img_{}.jpg'.format(int(current_time)), framePic)
            endtime = current_time

            ret0, buffer0 = cv2.imencode('.jpg', framePic0)
            ret1, buffer1 = cv2.imencode('.jpg', framePic1)

            jpg_as_text0 = base64.b64encode(buffer0)
            jpg_as_text1 = base64.b64encode(buffer1)
            flagPic = True
            #print("Ok!!!")
        if(flagUSBOk == True):
            out0.write(framePic0)
            out1.write(framePic1)    

          
                    #break 
        #out.write(frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if (current_time/1000) - startTime > 60*timeVDO:
            break 
        if(GPIO.input(4) == 0):
            break
    else:
        break

# Release everything if job is finished

print("Process time > "+str((current_time/1000) - startTime)+" sec")
if(flagUSBOk == True):    
    out0.release()
    out1.release()
cap0.release()
cap1.release()
print("Ok!!!")
GPIO.output(17,False) 
GPIO.cleanup()
KillPs = True
