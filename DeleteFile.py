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
vercurrent = subprocess.check_output('git rev-parse --verify HEAD', shell=True)
print 'Cur ver ' + vercurrent

vergit =  subprocess.check_output('git ls-remote https://github.com/izemkung/pihos | head -1 | cut -f 1', shell=True)
print 'Git ver '+ vergit
if vergit == vercurrent :
    print "version FW Ok!!!"   
if vergit != vercurrent and len(vercurrent) == len(vergit):
    print "Download FW "
    if os.path.exists("/home/pi/tmp") == True:
        print subprocess.check_output('sudo rm -rf /home/pi/tmp', shell=True) 
        time.sleep(10)   
    print subprocess.check_output('sudo git clone https://github.com/izemkung/pihos /home/pi/tmp', shell=True)
    time.sleep(10)
    if os.path.exists("/home/pi/tmp") == True:
        print subprocess.check_output('sudo rm -rf /home/pi/pihos', shell=True)
        #time.sleep(10)
        print subprocess.check_output('sudo mv /home/pi/tmp /home/pi/pihos', shell=True)
    #print subprocess.check_output('rm -rf /home/pi/tmp', shell=True)
    print "FW Ready to use!!!"
    exit()
    os.system('sudo reboot')
    #break
#continue

if os.path.exists("/home/pi/usb/vdo/ch0") == False:
    os.system('sudo mount /dev/sda1 /home/pi/usb')
    print 'Mount!!!'
    exit()

   
statvfs = os.statvfs('/home/pi/usb')
size = (statvfs.f_frsize * statvfs.f_blocks) / 1073741824.00
avail = (statvfs.f_frsize * statvfs.f_bavail) / 1073741824.00 
per = (( size - avail ) / size ) * 100
print '/home/pi/usb  Size = {0:.2f} Avail = {1:.2f} Use% = {2:.2f}'.format(size,avail,per)

#================================Delet PIC==================================
#print len([name for name in os.listdir('/home/pi/usb/pic/ch0') if os.path.isfile(os.path.join('/home/pi/usb/pic/ch0', name))])
#print min(glob.iglob('/home/pi/usb/pic/ch0/*.[Jj][Pp][Gg]'), key=os.path.getctime)
count = len([name for name in os.listdir('/home/pi/usb/pic/ch0') if os.path.isfile(os.path.join('/home/pi/usb/pic/ch0', name))]) 
numDel = 0 
print 'NUM Pic ch0 {0} '.format(count)
if count > 100: 
    while count > 50: 
        count = len([name for name in os.listdir('/home/pi/usb/pic/ch0') if os.path.isfile(os.path.join('/home/pi/usb/pic/ch0', name))]) 
        pic0 = min(glob.iglob('/home/pi/usb/pic/ch0/*.[Jj][Pp][Gg]'), key=os.path.getctime)
        count -= 1
        numDel += 1
        #print 'Delete' + pic0
        try:
            os.remove(pic0)
        except:
            print 'Delete error re mount 0'
            os.system('sudo mount /dev/sda1 -o remount,rw')
            os.system('sudo rm -r /home/pi/usb/pic/ch0')
            os.system('sudo mkdir /home/pi/usb/pic/ch0')


    #print subprocess.check_output('rm -r /home/pi/usb/pic/ch0/*', shell=True)    
    print 'Delete {0} file in pic/ch0/ '.format(numDel)
    
count = len([name for name in os.listdir('/home/pi/usb/pic/ch1') if os.path.isfile(os.path.join('/home/pi/usb/pic/ch1', name))])
numDel = 0
print 'NUM Pic ch1 {0} '.format(count)   
if  count > 100:
    while count > 50:
        count = len([name for name in os.listdir('/home/pi/usb/pic/ch1') if os.path.isfile(os.path.join('/home/pi/usb/pic/ch1', name))])
        pic1 = min(glob.iglob('/home/pi/usb/pic/ch1/*.[Jj][Pp][Gg]'), key=os.path.getctime) 
        count -= 1
        numDel += 1
        #print 'Delete' + pic1
        try:
            os.remove(pic1)
        except:
            print 'Delete error re mount 1'
            os.system('sudo mount /dev/sda1 -o remount,rw')
            os.system('sudo rm -r /home/pi/usb/pic/ch1')
            os.system('sudo mkdir /home/pi/usb/pic/ch1')
    #print subprocess.check_output('rm -r /home/pi/usb/pic/ch1/*', shell=True)    
    print 'Delete {0} file in pic/ch1/ '.format(numDel)
    
if per < 80 :
    print 'Memmory < 80% Ok!!'
    time.sleep(60)
    
if per > 50 :    
    while per > 30 :
        OldVideo0 = min(glob.iglob('/home/pi/usb/vdo/ch0/*.[Aa][Vv][Ii]'), key=os.path.getctime)
        OldVideo1 = min(glob.iglob('/home/pi/usb/vdo/ch1/*.[Aa][vv][Ii]'), key=os.path.getctime)

        #count = 0
        #for file in os.listdir("/home/pi/usb/pic/ch0/"):
            #if file.endswith(".jpg"):
                #if os.path.getctime("/home/pi/usb/pic/ch0/" + file) < os.path.getctime(OldVideo0) :
                    #os.remove("/home/pi/usb/pic/ch0/" + file)
                    #count = count +1
        try:
            os.remove(OldVideo0)
        except:
            print 'Delete VDO 0 re mount'
            os.system('sudo mount /dev/sda1 -o remount,rw')           
        
        print 'Delete '+ OldVideo0 
        print 'Delete {0} file in /home/pi/usb/pic/ch0/ '.format(count)

        #count = 0;
        #for file in os.listdir("/home/pi/usb/pic/ch1/"):
            #if file.endswith(".jpg"):
                #if os.path.getctime("/home/pi/usb/pic/ch1/" + file) < os.path.getctime(OldVideo1) :
                    #os.remove("/home/pi/usb/pic/ch1/" + file)
                    #count = count +1
                    
        try:
            os.remove(OldVideo1)
        except:
            print 'Delete VDO 1 re mount'
            os.system('sudo mount /dev/sda1 -o remount,rw') 
        print 'Delete '+ OldVideo1       
        print 'Delete {0} file in /home/pi/usb/pic/ch1/ '.format(count)

        statvfs = os.statvfs('/home/pi/usb')
        size = (statvfs.f_frsize * statvfs.f_blocks) / 1073741824.00
        avail = (statvfs.f_frsize * statvfs.f_bavail) / 1073741824.00 
        per = (( size - avail ) / size ) * 100
        print '/home/pi/usb  Size = {0:.2f} Avail = {1:.2f} Use% = {2:.2f}'.format(size,avail,per)
        
print 'Memmory is OK!!!'
time.sleep(300)
#print 'Memmory is Error'
