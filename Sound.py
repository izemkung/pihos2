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

version = 30
sound = "disable"#enable#disable
sound_level = 100
sound_time_OverSpeed = 60
over_Speed = 80
flagOverSpeed = False
timePlaySound = 0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#========For Sound=========
GPIO.setup(23, GPIO.OUT)#sound
GPIO.output(23,False)#disable sound

try:
  version = ConfigSectionMap('Profile')['version']
except:
  print("exception version")
print  'version > ',version

try:
  sound = ConfigSectionMap('Profile')['sound']
  over_Speed = ConfigSectionMap('Profile')['over_speed']
  sound_level = ConfigSectionMap('Profile')['sound_level']
  import pygame
  pygame.mixer.init()
  pygame.mixer.music.set_volume(float(sound_level)/100)
  pygame.mixer.music.load("alert.mp3")
  
except:
  print("exception pygame")
print  'sound > ',sound
print  'over_Speed > ',over_Speed
print  'sound_level > ',sound_level

gpsd = None #seting the global variable
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

gpsp = GpsPoller() # create the thread
gpsp.start() # start it up
countError = 0
timeReset = time.time() + 1200
timestart = time.time()
while True:
 
  time.sleep(0.95) #set to whatever

  if str(gpsd.fix.latitude) != 'nan' and str(gpsd.fix.latitude) != '0.0':
    print 'GPS Error ', countError , ' setting speed ',over_Speed, 'speed ',str(gpsd.fix.speed*3.6)
    if(str(gpsd.fix.speed) != 'nan' and str(gpsd.fix.speed) != 'NaN'):
        if(int(gpsd.fix.speed*3.6) > int(over_Speed)):
            if flagOverSpeed == False:
                timePlaySound = time.time()
            flagOverSpeed = True
        else:
            flagOverSpeed = False
            timePlaySound = time.time()

       
        if(flagOverSpeed == True and sound == "enable"):
            GPIO.output(23,True)#enable sound
            print 'Enter Play Sound'
            if(time.time() > timePlaySound+sound_time_OverSpeed):
                print 'Enter Play Sound with sound'
                try:
                    pygame.mixer.music.play()
                    print 'Play Over Speed'
                except:
                    print 'Play Sound except'
        else:
            GPIO.output(23,False)#disable sound

  else:
    countError += 1  

  if time.time() > timeReset:
    print "TimeReset"
    break
    
  if countError > 20:
    print "countError"
    break

gpsp.running = False
gpsp.join() # wait for the thread to finish what it's doing
GPIO.output(23,False)#disable sound
GPIO.cleanup()
print "Done.\nExiting."
exit()
