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
import cv
import base64
import requests
import urllib2
import httplib
import threading
import ConfigParser
import signal

class Timeout():
    """ Timeout for use with the `with` statement. """

    class TimeoutException(Exception):
        """ Simple Exception to be called on timeouts. """
        pass

    def _timeout(signum, frame):
        """ Raise an TimeoutException.

        This is intended for use as a signal handler.
        The signum and frame arguments passed to this are ignored.

        """
        raise Timeout.TimeoutException()

    def __init__(self, timeout=10):
        self.timeout = 10
        signal.signal(signal.SIGALRM, Timeout._timeout)

    def __enter__(self):
        signal.alarm(self.timeout)

    def __exit__(self, exc_type, exc_value, traceback):
        signal.alarm(0)
        return exc_type is Timeout.TimeoutException


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

config = 2
try:
  config =  ConfigSectionMap('Profile')['config']
except:
  print("exception config")

print 'config > ' , config

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

#print floderOk

flagUSBOk = False

if floderOk == 6:
    flagUSBOk = True
else:
    flagUSBOk = False

flagUSBOk = False

print("USB > "+str(flagUSBOk) + " Time VDO > "+str(timevdo)) 
os.environ['TZ'] = 'Asia/Bangkok'
time.tzset()
    


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
GPIO.setup(17,GPIO.OUT) #reg

KillPs = False
jpg_as_text0 = None
jpg_as_text1 = None
flagPic = False

def myThreadVDO ():
    global jpg_as_text0
    global jpg_as_text1
    global flagPic
    global KillPs
    global flagUSBOk
    global endtime

    cap0 = cv2.VideoCapture(0)
    cap1 = cv2.VideoCapture(1)

    out0 = None
    out1 = None
    #set the width and height, and UNSUCCESSFULLY set the exposure time
    #Config 

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
    h = 360
    w = 640
    fourcc = cv2.cv.CV_FOURCC('D','I','V','X')
    try:
        for num in range(0, 10):
            time.sleep(0.2)
            ret, frame = cap0.read()
            if ret == True :
                (h, w) = frame.shape[:2]
                print("Vdo:"+str(w)+"x"+str(h) + " Pic:"+str(w/picResolotion)+"x"+str(h/picResolotion) )
                break
    except:
        exit()

    vdoname = gmtime()

    if(flagUSBOk == True):
        out0 = cv2.VideoWriter('/home/pi/usb/vdo/ch0'+'/vdo_{}.avi'.format(strftime("%d%m%Y%H%M%S", vdoname)),fourcc, 20.0, (w,h))
        out1 = cv2.VideoWriter('/home/pi/usb/vdo/ch1'+'/vdo_{}.avi'.format(strftime("%d%m%Y%H%M%S", vdoname)),fourcc, 20.0, (w,h))
        print( 'vdo/chX/vdo_{}.avi'.format(strftime("%d%m%Y%H%M%S", vdoname))) 

    while(cap0.isOpened() and cap1.isOpened()):
        current_time = time.time() * 1000
        ret0, frame0 = cap0.read()
        ret1, frame1 = cap1.read()
        if(flagUSBOk == True):
            out0.write(frame0)
            out1.write(frame1)

        if ret0 == True and ret1 == True:
            
            if current_time - endtime > 100 and flagPic == False:
                framePic0 = imutils.resize(frame0, w/picResolotion)
                framePic1 = imutils.resize(frame1, w/picResolotion)
                cv2.putText(framePic0,"Ambulance "+ str(id) + " id 0"+" {}".format(strftime("%d %b %Y %H:%M:%S")) ,(2,(h/picResolotion) - 5), font, 0.3,(0,255,255),1)    
                cv2.putText(framePic1,"Ambulance "+ str(id) + " id 1"+" {}".format(strftime("%d %b %Y %H:%M:%S")) ,(2,(h/picResolotion) - 5), font, 0.3,(0,255,255),1)    
                
                #cv2.imwrite(args["output"]+  'pic/ch' +str(args["idcamera"])  +'/img_{}.jpg'.format(int(current_time)), framePic)
                endtime = current_time

                ret0, buffer0 = cv2.imencode('.png', framePic0)
                ret1, buffer1 = cv2.imencode('.png', framePic1)

                jpg_as_text0 = buffer0
                jpg_as_text1 = buffer1
                #jpg_as_text0 = base64.b64encode(buffer0)
                #jpg_as_text1 = base64.b64encode(buffer1)
                flagPic = True
                print("Capp!!!")
                
            
                        #break 
            #out.write(frame)
            
        if KillPs == True:
            break

    if(flagUSBOk == True):    
        out0.release()
        out1.release()
    cap0.release()
    cap1.release()
    print("T1 Kills")

current_time_T = 0
last_time_T = 0
countPic_T = 0
countPic_R = 0
connectionError = 0
while(GPIO.input(4) == 0):
    print("Pi Power Off Process!!")
    time.sleep(0.2)
    GPIO.output(17,True)
    time.sleep(0.2)
    GPIO.output(17,False)

t1 = threading.Thread(target=myThreadVDO)
t1.start()

while (True):
    current_time_T = time.time() * 1000
    
    if flagPic == True:
        if current_time_T - last_time_T > 500:
            last_time_T = current_time_T
            flagPic = False
            #GPIO.output(17,True)

            #url = "http://202.183.192.154:5000/api/tracking/postAmbulanceImageUpload"
            countPic_R += 1
            if (config == "2" and countPic_R % 20 != 0):
                url = "http://27.254.149.188:5000/api/snapshot/postAmbulanceImageUpload"
                payload={ 
                'ambulance_id':  str(id),
                'ambulance_box_code': str(id),
                'images_count': '2'
                } 
                jpg_as_text0 = jpg_as_text0.tostring()
                jpg_as_text1 = jpg_as_text1.tostring()
                jpg_as_text2 = ''
                jpg_as_text3 = ''
                files=[
                ('images_name_1',('im1.png',jpg_as_text0,'image/png')),
                ('images_name_2',('im2.png',jpg_as_text1,'image/png')),
                ('images_name_3',('im3.png',jpg_as_text2,'image/png')),
                ('images_name_4',('im4.png',jpg_as_text3,'image/png'))
                ]
                headers = {}
             
            else:
                url = pic_url
                headers = {}
                files = {}
                jpg_as_text0 = base64.b64encode(jpg_as_text0)
                jpg_as_text1 = base64.b64encode(jpg_as_text1)
                payload = {'ambulance_id':id,'images_name_1':jpg_as_text0,'images_name_2':jpg_as_text1}
            #dbSrver
            #url = "http://202.183.192.149:3000/fileupload"
            #payload={ 'ID': id,
            #'Time': '2',
            #'ambulance_id': str(id),
            #'ambulance_static_id': str(id),
            #'images_count': '2'}
            #files=[
            #('images_name_1',('im1.jpg',jpg_as_text0.tostring(),'image/jpg')),
            #('images_name_2',('im2.jpg',jpg_as_text1.tostring(),'image/jpg'))
            #]

            
            #flagPic = False
            try:
                GPIO.output(17,False)
                r = 'error'
                with Timeout(5):
                    r = requests.request("POST", url, headers=headers, data=payload, files=files)
                    #print('No timeout?')
                    print(r.text)
                    print(r.status_code)
                    connectionError = 0

                    if(r.status_code != 200 ):
                        print r
                
                    if flagUSBOk == False :
                        time.sleep(0.2)
                        GPIO.output(17,True)
                        time.sleep(0.2)
                        GPIO.output(17,False)
                        time.sleep(0.2)
                    
                    if(r.status_code == 200 ):
                        #time.sleep(0.2)
                        GPIO.output(17,True)
                        countPic_T += 1
                        print("Send > "+str(countPic_T)+" FreamRate > "+str((current_time_T - last_time_T))+" ms" + "Run Time > "+str((current_time_T/1000) - startTime) ) 
                    
            except:
                #print('timeout')
                connectionError += 1
                if connectionError > 10:
                    connectionError = 0
                    print "Connection Error or Time Out"
                    break
                    
           
            #print("Run Time > "+str((current_time_T/1000) - startTime) )
            #print("condi  > "+str(60 * int(timevdo) ))

    if ((current_time_T/1000) - startTime) > (60 * int(timevdo)):
        break 

    if (t1.isAlive() == False):
        print "Thread is not Alive"
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if (GPIO.input(4) == 0) :
        break

print("Time > "+str(timevdo) + " m NumPic > "+str(countPic_T)) 
KillPs = True

    #timeVDO
# Release everything if job is finished

print("Process time > "+str((current_time/1000) - startTime)+" sec")

GPIO.output(17,True)
GPIO.cleanup()
#t1.join()
print("End VDOS.py")