import argparse
import logging
import time
import requests
import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(level=logging.ERROR)

class Register(object):
    def __init__(self, url, wamp_port):
        # all robots share the same realm. No reason to separate them
        print("ws://%s:%s/ws"%(url,wamp_port), "realm1")
        self.runner = ApplicationRunner("ws://%s:%s/ws"%(url,wamp_port), "realm1")
    def add_sensor(self, sensor):
        self.runner.run(sensor)
    def add_control(self, control):
        self.runner.run(control)

class Signal(ApplicationSession):
    def __init__(self, url, web_port, wamp_port, robot_name, signal_name):
        self.url = url
        self.web_port = web_port
        self.wamp_port = wamp_port
        self.robot_name = robot_name
        self.signal_name = signal_name
        # All robots use the same realm. There's no reason to shield them from one another
        super(Signal, self).__init__()
    def get_channel_name(self):
        return '{}.{}'.format(self.robot_name, self.signal_name)
    def run_with_socket(self):
        raise NotImplementedError()
    def register_signal(self):
        raise NotImplementedError()
    def onJoin(self):
        self.register_signal()
        self.run_with_socket()
    def onDisconnect(self):
        asyncio.get_event_loop().stop()

class Control(Signal):
    def apply_control(self,signal):
        raise NotImplementedError()
    def get_limits(self):
        raise NotImplementedError()
    def register_signal(self):
        url = "{url}:{port}/robots/{robot_name}/controls/{control_name}".format(
            url=self.url,
            port=self.web_port,
            robot_name=self.robot_name,
            control_name=self.signal_name,
        )
        requests.post(url, data = {'channel_name':self.get_channel_name(),
                                    'limits':self.get_limits()})
    def run_with_socket(self):
        self.subscribe(self.apply_control, self.get_channel_name())

class Sensor(Signal):
    def get_reading(self):
        raise NotImplementedError()
    def get_mediatype(self):
        raise NotImplementedError()
    def register_signal(self):
        url = "{url}:{port}/robots/{robot_name}/sensors/{sensor_name}".format(
            url=self.url,
            port=self.web_port,
            robot_name=self.robot_name,
            sensor_name=self.signal_name,
        )
        requests.post(url, data = {'channel_name':self.get_channel_name(),
                                    'mediatype':self.get_mediatype()})
    def run_with_socket(self):
        while True:
            self.publish(self.get_channel_name(), self.get_reading())

