import serial
import time

while True:
    time.sleep(5)
    
port = 'Error'
for num in range(0, 4):
    port = '/dev/ttyUSB{0}'.format(num)
    try:
        ser = serial.Serial(port, 115200, timeout=.5)
        input = ser.inWaiting()
        print('Checking {0} Data In {1}'.format(port,input))
        time.sleep(5)
        input = ser.inWaiting()
    except:
        print('Port {0} busy'.format(port))
    try:
        for count in range(0, 10):
            print(ser.readline())
    except:
        print('Port {0} Except'.format(port))
    print('Checked {0} Data In {1}'.format(port,input))
    if(input > 500):
        print('{0} Ok!!!'.format(port))
        break
print('ERROR')
    