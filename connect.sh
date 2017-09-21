cd /
cd home/pi/3g
sudo /home/pi/3g/umtskeeper --sakisoperators "USBINTERFACE='3' OTHER='USBMODEM' USBMODEM='05c6:9003' APN="CUSTOM_APN" CUSTOM_APN="internet" APN_USER='ais' APN_PASS='ais'" --sakisswitches "--sudo --console" --devicename 'Huawei' --log --nat 'no' --httpserver
cd /

