#! /usr/bin/python
# Written by Dan Mandle http://dan.mandle.me September 2012
# License: GPL 2.0
 
import time
import RPi.GPIO as GPIO ## Import GPIO library

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(22, GPIO.OUT)#GPS
GPIO.setup(17, GPIO.OUT)#GPS
current_time = time.time() + 60
while True:
 GPIO.output(17,True)
 GPIO.output(22,True)
 time.sleep(2) #set to whatever
 GPIO.output(17,False)
 GPIO.output(22,False)
 time.sleep(1) #set to whatever
 if time.time() > current_time:
   break
  
GPIO.cleanup()
print "Done.\nExiting."
exit()
