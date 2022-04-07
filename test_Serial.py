import serial
import time

#while True:
#    time.sleep(5)


def FindSerialModem():
    _port = 'Error'
    for num in range(0, 4):
        _port = '/dev/ttyUSB{0}'.format(num)
        try:
            ser = serial.Serial(_port,115200, timeout=3.0 , rtscts=True, dsrdtr=True)
            ser.flushInput()
            ser.flushOutput()
            time.sleep(1)
            ser.write('AT\r')
            ser.write('AT\r')
            for num in range(0, 4):
                _bufin = ser.readline()
                print('Checking {0} Data In {1}'.format(_port,_bufin))
                if _bufin.count('OK'):
                    print('Found!! OK!!')
                    ser.close()
                    return _port
            ser.close()
            time.sleep(1)
        except:
            print('Port {0} busy'.format(_port))

    return _port

def FindGPS_SerialModem():
    _port = 'Error'
    for num in range(0, 4):
        _port = '/dev/ttyUSB{0}'.format(num)
        try:
            ser = serial.Serial(_port,115200, timeout=3.0 , rtscts=True, dsrdtr=True)
            for num in range(0, 4):
                _bufin = ser.readline()
                print('Checking {0} Data In {1}'.format(_port,_bufin))
                if _bufin.count('$'):
                    print('Found!! GPS!!')
                    ser.close()
                    return _port
            ser.close()
            time.sleep(1)
        except:
            print('Port {0} busy'.format(_port))

    return _port

print(FindSerialModem())
print(FindGPS_SerialModem())