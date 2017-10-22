import serial
import time

port = 'Error'
for num in range(0, 3):
    port = '/dev/ttyUSB{0}'.format(num)
    ser = serial.Serial(port, 115200, timeout=.5)
    input = ser.inWaiting()
    print('Checking {0} Data In {1}'.format(port,input))
    time.sleep(2)
    input = ser.inWaiting()
    print('Checked {0} Data In {1}'.format(port,input))
    if(input > 500):
        print('{0} Ok!!!'.format(port))
        break
    