import argparse
import logging
import time
import requests
import asyncio
import sys
import base64

from autobahn.asyncio.component import Component, run
from geppetto_client import Control, Sensor, Register

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(level=logging.ERROR)

class DummySensor(Sensor):
    def get_mediatype(self):
        return 'video'
    def get_reading(self):
        if not hasattr(self,'bytes'):
            self.bytes = bytes(open('./mountain.jpg','rb').read())
        return self.bytes

class DummyControl(Control):
    def get_limits(self):
        return 0,180
    def apply_control(self, control_info):
        print('applying control: %s: %s'%(self.channel_name, control_info))
        sys.stdout.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost', help='The host that geppetto is running on')
    parser.add_argument('--web-port', default=8080, type=int, help='The port that the geppetto web server is running on')
    parser.add_argument('--wamp-port', default=5555, type=int, help='The port that the geppetto wamp server is running on')
    args = parser.parse_args()

    # Register is in charge of adding/removing robots from the rest api
    with Register(args.host, args.web_port, args.wamp_port) as reg:
        # robot 1
        reg.add_sensor (DummySensor ('mock-robot1','sensor1'))
        reg.add_sensor (DummySensor ('mock-robot1','sensor2'))
        reg.add_control(DummyControl('mock-robot1','control1'))
        reg.add_control(DummyControl('mock-robot1','control2'))
        # robot 2
        reg.add_sensor (DummySensor ('mock-robot2','sensor1'))
        reg.add_sensor (DummySensor ('mock-robot2','sensor2'))
        reg.add_control(DummyControl('mock-robot2','control1'))
        reg.add_control(DummyControl('mock-robot2','control2'))
        ## interleave control/sensor logic with asyncio
        reg.start_with_asyncio()
        # run each control/sensor in its own process
        #reg.start_with_multiprocessing()
