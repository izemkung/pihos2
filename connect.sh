cd /
sudo systemctl stop gpsd.socket
sudo systemctl disable gpsd.socket
sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock
sudo systemctl enable gpsd.socket
sudo systemctl start gpsd.socket
cd /
cd home/pi/3g
sudo /home/pi/3g/umtskeeper --sakisoperators "USBINTERFACE='3' OTHER='USBMODEM' USBMODEM='05c6:9003' APN="CUSTOM_APN" CUSTOM_APN="internet" APN_USER='tely360' APN_PASS='tely360'" --sakisswitches "--sudo --console" --devicename 'U20' --log --nat 'no' --httpserver
cd /

