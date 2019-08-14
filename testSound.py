#! /usr/bin/python
# Written by Dan Mandle http://dan.mandle.me September 2012
# License: GPL 2.0
 
import os
import requests
from time import *
import time
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
sound = "disable"#enable#disable
sound_level = 100
sound_time_loop = 7
over_Speed = 80
flagOverSpeed = False
timePlaySound = 0

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
  pygame.mixer.music.set_volume(sound_level/100)
  pygame.mixer.music.load("alert.mp3")
  GPIO.setup(23, GPIO.OUT)#sound
  GPIO.output(23,False)#disable sound
except:
  print("exception pygame")
print  'sound > ',sound
print  'over_Speed > ',over_Speed
print  'sound_level > ',sound_level

gpsd = None #seting the global variable
timeout = None
timeReset = None


#checking port
#port = 'Error'



if(flagOverSpeed == True and sound == "enable"):
    GPIO.output(23,True)#enable sound
if(time.time() > timePlaySound):
    timePlaySound = time.time() + sound_time_loop
    try:
    pygame.mixer.music.play()
    except:
    print 'Play Sound Error'
else:
    GPIO.output(23,False)#disable sound


print "Done.\nExiting."
gpsp.running = False
gpsp.join() # wait for the thread to finish what it's doing
if version == '25':
  GPIO.output(27,False)
GPIO.output(22,False)
GPIO.cleanup()
exit()
