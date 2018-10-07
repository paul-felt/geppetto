import argparse
import logging
import time
import requests
import asyncio

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(level=logging.ERROR)

class Register(object):
    def __init__(self, url, port):
        self.url = url
        self.port = port

    def control_url(robot_name, control_name):
        return "{url}:{port}/robots/{robot_name}/controls/{control_name}".format(
            url=self.url,
            port=self.web_port,
            robot_name=robot_name,
            control_name=control_name,
        )
    def sensor_url(robot_name, sensor_name):
        return "{url}:{port}/robots/{robot_name}/sensors/{sensor_name}".format(
            url=self.url,
            port=self.web_port,
            robot_name=robot_name,
            sensor_name=sensor_name,
        )

    def __enter__(self):
        ' Just make sure the rest interface responds in the most basic way '
        requests.get("{url}:{port}/robots".format(
            url=self.url,
            port=self.web_port,
        ))
    def __exit__(self, type, value, traceback):
        ' Delete from the rest api all sensors and controls in this register '
        for robot_name, sensor_name in self.sensors:
            url = self.sensor_url(robot_name, sensor_name)
            requests.delete(url)
        for robot_name, control_name in self.controls:
            url = self.control_url(robot_name, control_name)
            requests.delete(url)
        # TODO: delete robot itself if necessary

    def add_sensor(self, sensor):
        url = self.sensor_url(sensor.robot_name, sensor.sensor_name)
        requests.post(url, data = {'channel_name':self.channel_name,
                                    'mediatype':self.get_mediatype()})
    def add_control(self, control):
        url = self.control_url(control.robot_name, control.control_name)
        requests.post(url, data = {'channel_name':self.channel_name,
                                    'limits':self.get_limits()})

class Signal(ApplicationSession):
    def __init__(self, robot_name, signal_name):
        self.robot_name = robot_name
        self.signal_name = signal_name
        self.channel_name = '{}.{}'.format(self.robot_name, self.signal_name)
    def run(self, session):
        raise NotImplementedError()

class Control(Signal):
    def apply_control(self,signal):
        raise NotImplementedError()
    def get_limits(self):
        raise NotImplementedError()
    async def run(self, session):
        self.subscribe(self.apply_control, self.channel_name)
        while True:
            await asyncio.sleep(0)

class Sensor(Signal):
    def get_reading(self):
        raise NotImplementedError()
    def get_mediatype(self):
        raise NotImplementedError()
    async def run(self, session):
        while True:
            await self.publish(self.channel_name, self.get_reading())

