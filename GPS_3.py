#! /usr/bin/python
# Written by Dan Mandle http://dan.mandle.me September 2012
# License: GPL 2.0
 
import os
import requests
from gps import *
from time import *
import time
import threading
import RPi.GPIO as GPIO ## Import GPIO library
import serial
import time
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

    
Config = ConfigParser.ConfigParser()
Config.read('/home/pi/config.ini')

id =  ConfigSectionMap('Profile')['id']
timevdo = ConfigSectionMap('Profile')['timevdo']
timepic = ConfigSectionMap('Profile')['timepic']
gps_url = ConfigSectionMap('Profile')['gps_api']
pic_url = ConfigSectionMap('Profile')['pic_api']
version = 30

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

try:
  version = ConfigSectionMap('Profile')['version']
except:
  print("exception version")
print  'version > ',version


gpsd = None 
timeout = None
timeReset = None


class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

print  'URL > ',gps_url,' ID > ',id
gpsp = GpsPoller() # create the thread


if version == '25':
  GPIO.setup(27, GPIO.OUT)#3G
  print  'setGPIO 27 '

GPIO.setup(22, GPIO.OUT)#GPS

gpsp.start() # start it up
countSend = 0
countError = 0
timeout = time.time() + 30
timeReset = time.time() + 1200

while True:
 
  print 'GPS sending Seccess ' , countSend ,' Error ', countError  
  #print '----------------------------------------'
  #print 'latitude    ' , gpsd.fix.latitude
  #print 'longitude   ' , gpsd.fix.longitude
  #print 'time utc    ' , gpsd.utc,' + ', gpsd.fix.time
  #print 'Heading     ' , gpsd.fix.track,'deg (true)'
  #print  gps_url,'?ambulance_id={0}&tracking_latitude={1:.6f}&tracking_longitude={2:.6f}&tracking_speed={3:.2f}'.format(id,gpsd.fix.latitude,gpsd.fix.longitude,gpsd.fix.speed)
        
  #print  gps_url,'?ambulance_id={0}&tracking_latitude={1:.6f}&tracking_longitude={2:.6f}&tracking_speed={3:.2f}&tracking_heading={4}'.format(id,gpsd.fix.latitude,gpsd.fix.longitude,gpsd.fix.speed,gpsd.fix.track)
  #http://safetyam.tely360.com/api/tracking1.php?ambulance_id=99&tracking_latitude=1.1&tracking_longitude=1.1&tracking_speed=60&tracking_heading=100
  
  if str(gpsd.fix.latitude) != 'nan' and str(gpsd.fix.latitude) != '0.0':
    GPIO.output(22,True)
    try:
      resp = requests.get(gps_url+'?ambulance_id={0}&tracking_latitude={1:.6f}&tracking_longitude={2:.6f}&tracking_speed={3:.2f}&tracking_heading={4}'.format(id,gpsd.fix.latitude,gpsd.fix.longitude,gpsd.fix.speed,gpsd.fix.track), timeout=2.001)
      
      if(resp.status_code != 200 ):
        print 'status_code ' , resp.status_code
      #print 'headers     ' , resp.headers
      #print 'content     ' , resp.content
      #GPIO.output(27,True)
      if(resp.status_code == 200 ):
        countSend += 1
        countError = 0
        timeout = time.time() + 30 #timeout reset
        if version == '25':
          GPIO.output(27,True)
      else:
        print 'respError'
        countError+=1

    except:
      print 'exceptError'
      countError += 1
  else:
    countError += 1  
    
  GPIO.output(22,False)
  time.sleep(0.95) #set to whatever

  if time.time() > timeout:
    print "Timeout"
    for count in range(0, 2):
      time.sleep(0.5)
      GPIO.output(22,True)
      time.sleep(2)
      GPIO.output(22,False)
    break

  if time.time() > timeReset:
    print "TimeReset"
    for count in range(0, 2):
      time.sleep(0.5)
      GPIO.output(22,True)
      time.sleep(0.5)
      GPIO.output(22,False)
    break
    
  if countError > 20:
    print "countError"
    for count in range(0, 10):
      time.sleep(0.2)
      GPIO.output(22,True)
      time.sleep(0.2)
      GPIO.output(22,False)
      if version == '25':
        GPIO.output(27,False)
    break

  #print 'altitude (m)' , gpsd.fix.altitude
    #print 'eps         ' , gpsd.fix.eps
    #print 'epx         ' , gpsd.fix.epx
    #print 'epv         ' , gpsd.fix.epv
    #print 'ept         ' , gpsd.fix.ept
    #print 'speed (m/s) ' , gpsd.fix.speed
    #print 'climb       ' , gpsd.fix.climb
    #print 'track       ' , gpsd.fix.track
    #print 'mode        ' , gpsd.fix.mode
    #print
    #print 'sats        ' , gpsd.satellites
    
  
  #r = urllib.request.urlopen('https://api.github.com', auth=('user', 'pass'))
  #var r = requests.get('http://www.google.com')
  
    

#except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
  #print "\nKilling Thread..."
  #gpsp.running = False
  #gpsp.join() # wait for the thread to finish what it's doing
  #GPIO.output(27,False)
  #GPIO.output(22,False)
  #GPIO.cleanup()
  #exit()


gpsp.running = False
gpsp.join() # wait for the thread to finish what it's doing
if version == '25':
  GPIO.output(27,False)
GPIO.output(22,False)
GPIO.cleanup()
print "Done.\nExiting."
exit()
