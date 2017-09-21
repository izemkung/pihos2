import os
import glob
import cv2
import cv
import datetime
import base64
import requests
import urllib2
import httplib
import time
import sys
import subprocess

#===================================================Update FW Version================================
vercurrent = subprocess.check_output('sudo rm /home/pi/usb/pic/ch0/*.jpg', shell=True)
print vercurrent
print '0 >'+ vercurrent.split(':')[0]
print '1 >'+ vercurrent.split(':')[1]
print '2 >'+ vercurrent.split(':')[2]
if vercurrent == '' :
    print 'isOK' + vercurrent

