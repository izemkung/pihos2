from time import gmtime, strftime
import RPi.GPIO as GPIO ## Import GPIO library
import time
import datetime
import imutils
import numpy as np
import cv2
import argparse
import os
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

if os.path.exists("/home/pi/usb/config.ini") == False:
    print("config.ini error")
    os.system('sudo mount /dev/sda1 /home/pi/usb')
    exit()
    
Config = ConfigParser.ConfigParser()
Config.read('/home/pi/usb/config.ini')

id =  ConfigSectionMap('Profile')['id']
timevdo = ConfigSectionMap('Profile')['timevdo']
timepic = ConfigSectionMap('Profile')['timepic']

print("ID "+ id + " TimeVdo " + timevdo + " TimePic " + timepic) 

if os.path.exists("/home/pi/usb/vdo") == False:
    os.system('sudo mkdir /home/pi/usb/vdo')
if os.path.exists("/home/pi/usb/vdo/ch0") == False:
    os.system('sudo mkdir /home/pi/usb/vdo/ch0')
if os.path.exists("/home/pi/usb/vdo/ch1") == False:
    os.system('sudo mkdir /home/pi/usb/vdo/ch1')
if os.path.exists("/home/pi/usb/pic") == False:
    os.system('sudo mkdir /home/pi/usb/pic')
if os.path.exists("/home/pi/usb/pic/ch0") == False:
    os.system('sudo mkdir /home/pi/usb/pic/ch0')
if os.path.exists("/home/pi/usb/pic/ch1") == False:
    os.system('sudo mkdir /home/pi/usb/pic/ch1')

os.environ['TZ'] = 'Asia/Bangkok'
time.tzset()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) ## Use board pin numbering
GPIO.setup(4, GPIO.IN) # Power
GPIO.setup(17,GPIO.OUT)


def myThreadCam0 ():
    while(GPIO.input(4) == 0):
        print("Ok!!!")
        time.sleep(0.2)
        GPIO.output(17,True)
        time.sleep(0.2)
        GPIO.output(17,False)

    print("Camera0") 
    cap0 = cv2.VideoCapture(0)
    cap0.set(3,1360/2)
    cap0.set(4,768/2)
    cap0.set(5,20)
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

    vdoname =  gmtime()
    out0 = cv2.VideoWriter('/home/pi/usb/vdo/ch0/vdo_{}.avi'.format(strftime("%d%m%Y%H%M%S", vdoname)),fourcc, 20.0, (w,h))
    print('/home/pi/usb/vdo/ch0/vdo_{}.avi'.format(strftime("%d%m%Y%H%M%S", vdoname))) 

    #Picture 
    current_time = 0
    countPic = 0
    endtime = 0
    framePic = None 
    startTime = time.time()

    font = cv2.FONT_HERSHEY_SIMPLEX
    print("Cam0 TimeVdo " + timevdo + " TimePic " + timepic) 
    while(cap0.isOpened()):
        current_time = time.time()
        ret, frame = cap0.read()
        if ret==True:
            if current_time - endtime > timepic:
                framePic = imutils.resize(frame, w/picResolotion)
                cv2.putText(framePic,"Ambulance "+ str(id) + " id 0 {}".format(strftime("%d %b %Y %H:%M:%S")) ,(2,(h/picResolotion) - 5), font, 0.3,(0,255,255),1)    
                
                cv2.imwrite('/home/pi/usb/pic/ch0/img_{}.jpg'.format(strftime("%d%m%Y%H%M%S")), framePic)
                endtime = current_time
                countPic+=1
                print("pic0 Save" + countPic) 
            
            out0.write(frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if current_time - startTime > 60*timevdo:
                break 
            if(GPIO.input(4) == 0):
                break
        else:
            break

    # Release everything if job is finished
    print("Time > "+str(timevdo) + " m NumPic > "+str(countPic)) 
    print("Process time > "+str(current_time - startTime)+" sec")
    out.release()
    cap.release()
    print("Ok!!!") 
    GPIO.cleanup()

def myThreadCam1 ():
    while(GPIO.input(4) == 0):
        print("Ok!!!")
        time.sleep(0.2)
        GPIO.output(17,True)
        time.sleep(0.2)
        GPIO.output(17,False)

    print("Camera1") 
    cap1 = cv2.VideoCapture(1)
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
    ret, frame = cap1.read()
    (h, w) = frame.shape[:2]
    print("Vdo:"+str(w)+"x"+str(h) + " Pic:"+str(w/picResolotion)+"x"+str(h/picResolotion) )

    vdoname =  gmtime()
    out1 = cv2.VideoWriter('/home/pi/usb/vdo/ch1/vdo_{}.avi'.format(strftime("%d%m%Y%H%M%S", vdoname)),fourcc, 20.0, (w,h))
    print('/home/pi/usb/vdo/ch1/vdo_{}.avi'.format(strftime("%d%m%Y%H%M%S", vdoname))) 

    #Picture 
    current_time = 0
    countPic = 0
    endtime = 0
    framePic = None 
    startTime = time.time()

    font = cv2.FONT_HERSHEY_SIMPLEX
    print("Cam1 TimeVdo " + timevdo + " TimePic " + timepic) 
    while(cap1.isOpened()):
        current_time = time.time()
        ret, frame = cap1.read()
        if ret==True:
            if current_time - endtime > timepic:
                framePic = imutils.resize(frame, w/picResolotion)
                cv2.putText(framePic,"Ambulance "+ str(id) + " id 0 {}".format(strftime("%d %b %Y %H:%M:%S")) ,(2,(h/picResolotion) - 5), font, 0.3,(0,255,255),1)    
                
                cv2.imwrite('/home/pi/usb/pic/ch1/img_{}.jpg'.format(strftime("%d%m%Y%H%M%S")), framePic)
                endtime = current_time
                countPic+=1
                print("pic1 Save" + countPic) 
            
            out1.write(frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if current_time - startTime > 60*timevdo:
                break 
            if(GPIO.input(4) == 0):
                break
        else:
            break

    # Release everything if job is finished
    print("Time > "+str(timevdo) + " m NumPic > "+str(countPic)) 
    print("Process time > "+str(current_time - startTime)+" sec")
    out.release()
    cap.release()
    print("Ok!!!") 
    GPIO.cleanup()


t1 = threading.Thread(target=myThreadCam1)
t2 = threading.Thread(target=myThreadCam0)
t1.start()
t2.start()

while(GPIO.input(4) == 0):
    if(t1.isAlive() == false):
        t1.start()
    if(t2.isAlive() == false):
        t2.start()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        t2.kill()
        t2.kill()
        break