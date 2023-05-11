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

def updateAPN():
    print ('updateAPN ')
    config_path = '/home/pi/apn_configure.cfg'
    file_exists = os.path.exists(config_path)
    apn_string_list = ''
    apn=''
    apnUser=''
    apnPass=''
    if(file_exists):
        print("Config found!!")
        usb_apn_file = open(config_path)
        apn_string_list = usb_apn_file.readlines()
        usb_apn_file.close()
        for idx in range(0, len(apn_string_list)):
            line = apn_string_list[idx]
            if 'apn=' in line:
                first_idx = line.find('=') + 1
                apn = line[first_idx:].strip('\n')
                print('APN : '+ apn)
            if 'apnUser=' in line:
                first_idx = line.find('=') + 1
                apnUser = line[first_idx:].strip('\n')
                print('apnUser : '+ apnUser)

            if 'apnPass=' in line:
                first_idx = line.find('=') + 1
                apnPass = line[first_idx:].strip('\n')
                print('apnPass : '+ apnPass)
            
            if 'anp' in line:
                os.system('sudo rm /home/pi/apn_configure.cfg')
    else:
        print("Config not found!!")
        return

    my_file_path =  "/home/pi/pihos/connect.sh"
    my_file = open(my_file_path)
    string_list = my_file.readlines()
    my_file.close()
    for idx in range(0, len(string_list)):
        line = string_list[idx]
        if 'umtskeeper' in line:
            first_idx = line.find('CUSTOM_APN=') + 12
            currentID = line[first_idx: line.find('APN_USER=')-2]
            print('current APN : '+ currentID)
            if( currentID != apn ):
                print("Update APN "+currentID+" > "+ apn)
                string_list[idx] = 'sudo /home/pi/3g/umtskeeper --sakisoperators "USBINTERFACE=\'3\' OTHER=\'USBMODEM\' USBMODEM=\'05c6:9003\' APN="CUSTOM_APN" CUSTOM_APN="'+ apn +'" APN_USER=\'tely360\' APN_PASS=\'tely360\'" --sakisswitches "--sudo --console" --devicename \'U20\' --log --nat \'no\' --httpserver'+'\n'
            #sudo ./quectel-CM -s tely360
            #    print(string_list[idx])
                my_file = open(my_file_path, "w")
                new_file_contents = "".join(string_list)
                my_file.write(new_file_contents)
                my_file.close()
                print("Update APN Reboot")
                os.system('sudo reboot')
                #reconnect camera
            else:
                print("Current APN = new APN : " + apn)


#===================================================Update FW Version================================
vercurrent = subprocess.check_output('git rev-parse --verify HEAD', shell=True)
print 'Cur ver ' + vercurrent

vergit =  subprocess.check_output('git ls-remote https://github.com/izemkung/pihos2 | head -1 | cut -f 1', shell=True)
print 'Git ver '+ vergit
if vergit == vercurrent :
    print "version FW Ok!!!"   
if vergit != vercurrent and len(vercurrent) == len(vergit):
    print "Download FW "
    if os.path.exists("/home/pi/tmp") == True:
        print subprocess.check_output('sudo rm -rf /home/pi/tmp', shell=True) 
        time.sleep(5)   
    print subprocess.check_output('sudo git clone https://github.com/izemkung/pihos2 /home/pi/tmp', shell=True)
    time.sleep(10)
    if os.path.exists("/home/pi/tmp") == True:
        print subprocess.check_output('sudo rm -rf /home/pi/pihos', shell=True)
        #time.sleep(10)
        print subprocess.check_output('sudo mv /home/pi/tmp /home/pi/pihos', shell=True)
    #print subprocess.check_output('rm -rf /home/pi/tmp', shell=True)
    print "FW Ready to use!!!"
    os.system('sudo reboot')
    #break
#continue


#================================APN UPDATE==================================
if os.path.exists("/home/pi/apn_configure.cfg") == False:
    os.system('sudo cp /home/pi/pihos/apn_configure.cfg /home/pi/apn_configure.cfg')
    print 'Move Defult apn_configs'
    
if os.path.exists("/home/pi/usb/apn_configure.cfg") == True:
    os.system('sudo rm -rf /home/pi/apn_configure.cfg')
    os.system('sudo cp /home/pi/usb/apn_configure.cfg /home/pi/apn_configure.cfg')
    print 'Found APN apn_configs on USB!!!'
updateAPN()


#if os.path.exists("/home/pi/usb/vdo/ch0") == False:
os.system('sudo mount /dev/sda1 /home/pi/usb')
time.sleep(1)

statvfs = os.statvfs('/home/pi/usb')
size = (statvfs.f_frsize * statvfs.f_blocks) / 1073741824.00
avail = (statvfs.f_frsize * statvfs.f_bavail) / 1073741824.00 
per = (( size - avail ) / size ) * 100
print '/home/pi/usb  Size = {0:.2f} Avail = {1:.2f} Use% = {2:.2f}'.format(size,avail,per)



#================================Delet PIC==================================
try:
    count = len([name for name in os.listdir('/home/pi/usb') if os.path.isfile(os.path.join('/home/pi/usb', name))])
    while count > 5:
        count = len([name for name in os.listdir('/home/pi/usb') if os.path.isfile(os.path.join('/home/pi/usb', name))])
        VideoREC = min(glob.iglob('/home/pi/usb/*.[Rr][Ee][Cc]'), key=os.path.getctime)
        os.remove(VideoREC)
        print 'Delete Rec'+ VideoREC 
except:
    print 'No file Rec' 
#print len([name for name in os.listdir('/home/pi/usb/pic/ch0') if os.path.isfile(os.path.join('/home/pi/usb/pic/ch0', name))])
#print min(glob.iglob('/home/pi/usb/pic/ch0/*.[Jj][Pp][Gg]'), key=os.path.getctime)
try:
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
                time.sleep(10)


        #print subprocess.check_output('rm -r /home/pi/usb/pic/ch0/*', shell=True)    
        print 'Delete {0} file in pic/ch0/ '.format(numDel)
        
    count = len([name for name in os.listdir('/home/pi/usb/pic/ch1') if os.path.isfile(os.path.join('/home/pi/usb/pic/ch1', name))])
    numDel = 0
    print 'NUM Pic ch1 {0} '.format(count)   
    if  count > 100:
        while count > 50:
            
            #print 'Delete' + pic1
            try:
                count = len([name for name in os.listdir('/home/pi/usb/pic/ch1') if os.path.isfile(os.path.join('/home/pi/usb/pic/ch1', name))])
                pic1 = min(glob.iglob('/home/pi/usb/pic/ch1/*.[Jj][Pp][Gg]'), key=os.path.getctime) 
                count -= 1
                numDel += 1
                os.remove(pic1)
            except:
                print 'Delete error re mount 1'
                os.system('sudo mount /dev/sda1 -o remount,rw')
                os.system('sudo rm -r /home/pi/usb/pic/ch1')
                os.system('sudo mkdir /home/pi/usb/pic/ch1')
                time.sleep(10)
        #print subprocess.check_output('rm -r /home/pi/usb/pic/ch1/*', shell=True)    
        print 'Delete {0} file in pic/ch1/ '.format(numDel)
        
    if per < 80 :
        print 'Memmory < 80% Ok!!'

        vdoFileError = True
        while(vdoFileError):
            vdoFileError = False
            try:
                OldVideo0 = min(glob.iglob('/home/pi/usb/vdo/ch0/*.[Aa][Vv][Ii]'), key=os.path.getsize)
                OldVideo1 = min(glob.iglob('/home/pi/usb/vdo/ch1/*.[Aa][vv][Ii]'), key=os.path.getsize)
                #print("Size (In bytes) of '%s':" %OldVideo1, os.path.getsize(OldVideo0) ) 
                #print("Size (In bytes) of '%s':" %OldVideo0, os.path.getsize(OldVideo1) ) 
                if(os.path.getsize(OldVideo0) < 50000):
                    os.remove(OldVideo0)
                    print("Remove : '%s'" %OldVideo0) 
                    vdoFileError = True

                if(os.path.getsize(OldVideo1) < 50000):
                    os.remove(OldVideo1)
                    print("Remove : '%s'" %OldVideo1) 
                    vdoFileError = True

            except:
                vdoFileError = True

            time.sleep(1)

        time.sleep(60)
        
    if per > 80 :    
        while per > 50 :
            

            #count = 0
            #for file in os.listdir("/home/pi/usb/pic/ch0/"):
                #if file.endswith(".jpg"):
                    #if os.path.getctime("/home/pi/usb/pic/ch0/" + file) < os.path.getctime(OldVideo0) :
                        #os.remove("/home/pi/usb/pic/ch0/" + file)
                        #count = count +1
            try:
                OldVideo0 = min(glob.iglob('/home/pi/usb/vdo/ch0/*.[Aa][Vv][Ii]'), key=os.path.getctime)
                OldVideo1 = min(glob.iglob('/home/pi/usb/vdo/ch1/*.[Aa][vv][Ii]'), key=os.path.getctime)
                os.remove(OldVideo0)
                print 'Delete '+ OldVideo0 
                print 'Delete {0} file in /home/pi/usb/pic/ch0/ '.format(count)
            except:
                print 'Delete VDO 0 re mount'
                os.system('sudo mount /dev/sda1 -o remount,rw')           
                time.sleep(10)
            

            #count = 0;
            #for file in os.listdir("/home/pi/usb/pic/ch1/"):
                #if file.endswith(".jpg"):
                    #if os.path.getctime("/home/pi/usb/pic/ch1/" + file) < os.path.getctime(OldVideo1) :
                        #os.remove("/home/pi/usb/pic/ch1/" + file)
                        #count = count +1
                        
            try:
                os.remove(OldVideo1)
                print 'Delete '+ OldVideo1       
                print 'Delete {0} file in /home/pi/usb/pic/ch1/ '.format(count)
            except:
                print 'Delete VDO 1 re mount'
                os.system('sudo mount /dev/sda1 -o remount,rw') 
                time.sleep(10)
            

            statvfs = os.statvfs('/home/pi/usb')
            size = (statvfs.f_frsize * statvfs.f_blocks) / 1073741824.00
            avail = (statvfs.f_frsize * statvfs.f_bavail) / 1073741824.00 
            per = (( size - avail ) / size ) * 100
            print '/home/pi/usb  Size = {0:.2f} Avail = {1:.2f} Use% = {2:.2f}'.format(size,avail,per)
except:
    print 'Delete Error'     
print 'Memmory is OK!!!'
time.sleep(300)
#print 'Memmory is Error'
