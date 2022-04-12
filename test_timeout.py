import signal

class Timeout():
    """ Timeout for use with the `with` statement. """

    class TimeoutException(Exception):
        """ Simple Exception to be called on timeouts. """
        pass

    def _timeout(signum, frame):
        """ Raise an TimeoutException.

        This is intended for use as a signal handler.
        The signum and frame arguments passed to this are ignored.

        """
        raise Timeout.TimeoutException()

    def __init__(self, timeout=10):
        self.timeout = 10
        signal.signal(signal.SIGALRM, Timeout._timeout)

    def __enter__(self):
        signal.alarm(self.timeout)

    def __exit__(self, exc_type, exc_value, traceback):
        signal.alarm(0)
        return exc_type is Timeout.TimeoutException

# Demonstration:
from time import sleep
import requests

url = "http://27.254.149.188:5000/api/crash/postAmbulanceCrashNotify"
payload={'ambulance_id': 99,
'tracking_latitude': 1.0,
'tracking_longitude': 1.0,
'tracking_heading': 1.0,
'tracking_speed': 1.0}
files=[]
headers = {}

resp = requests.request("POST", url, headers=headers, data=payload, files=files , timeout=(3.0,3.0))

print ('content     ' + resp.content) 

print 'SendAlartFun Connection lost'

print('This is going to take maximum 10 seconds...')

try:
    with Timeout(10):
        sleep(11)
        print('No timeout?')
except:
    print('timeout')
print('Done')


    