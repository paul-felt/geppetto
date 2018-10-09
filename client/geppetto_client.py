import argparse
import logging
import time
import requests
import asyncio
import autobahn

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(level=logging.ERROR)

logger = logging.getLogger(__name__)

class Signal(object):
    def __init__(self, robot_name, name, refresh=0.2):
        self.robot_name = robot_name
        self.name = name
        self.refresh = refresh
        self.channel_name = '{}.{}'.format(self.robot_name, self.name)
    def __repr__(self):
        return self.channel_name

class Control(Signal):
    def apply_control(self,signal):
        raise NotImplementedError()
    def get_limits(self):
        raise NotImplementedError()
    async def run(self, session, details):
        logger.info('subscribing to control: %s',self.channel_name)
        session.subscribe(self.apply_control, self.channel_name)

class Sensor(Signal):
    def get_reading(self):
        raise NotImplementedError()
    def get_mediatype(self):
        raise NotImplementedError()
    async def run(self, session, details):
        logger.info('publishing to sensor: %s',self.channel_name)
        while True:
            session.publish(self.channel_name, self.get_reading())
            await asyncio.sleep(self.refresh)

class Register(object):
    def __init__(self, host, web_port, wamp_port):
        self.host = host
        self.web_port = web_port
        self.wamp_port = wamp_port
        self.sensors = set([])
        self.controls = set([])

    def control_url(self, robot_name, name):
        return "http://{host}:{port}/robots/{robot_name}/controls/{name}".format(
            host=self.host,
            port=self.web_port,
            robot_name=robot_name,
            name=name,
        )

    def sensor_url(self, robot_name, name):
        return "http://{host}:{port}/robots/{robot_name}/sensors/{name}".format(
            host=self.host,
            port=self.web_port,
            robot_name=robot_name,
            name=name,
        )

    def __enter__(self):
        ' Just make sure the rest interface responds in the most basic way '
        requests.get("http://{host}:{port}/robots".format(
            host=self.host,
            port=self.web_port,
        ))
        return self

    def __exit__(self, type, value, traceback):
        ' Delete from the rest api all sensors and controls in this register '
        for sensor in self.sensors:
            url = self.sensor_url(sensor.robot_name, sensor.name)
            resp = requests.delete(url)
            assert resp.status_code == 200, 'sensor deletion request failed: %s'%resp.text
        for control in self.controls:
            url = self.control_url(control.robot_name, control.name)
            resp = requests.delete(url)
            assert resp.status_code == 200, 'control deletion request failed: %s'%resp.text
        # TODO: delete robot itself if necessary

    def add_sensor(self, sensor):
        url = self.sensor_url(sensor.robot_name, sensor.name)
        resp = requests.post(url, json = {'channel_name':sensor.channel_name,
                                    'mediatype':sensor.get_mediatype()})
        assert resp.status_code == 200, 'sensor creation request failed: %s'%resp.text
        self.sensors.add(sensor)

    def add_control(self, control):
        url = self.control_url(control.robot_name, control.name)
        resp = requests.post(url, json = {'channel_name':control.channel_name,
                                    'limits':control.get_limits()})
        assert resp.status_code == 200, 'control creation request failed: %s'%resp.text
        self.controls.add(control)

    def run(self):
        # define a wamp component with settings matching
        # the vanilla server settings (no special needs here)
        wamp_component = autobahn.asyncio.component.Component(
            transports=u"ws://{host}:{port}/ws".format(host=self.host, port=self.wamp_port),
            realm=u"realm1",
        )

        # callback controls
        for control in self.controls:
            wamp_component.on_join(control.run)

        # callback sensors
        for sensor in self.sensors:
            wamp_component.on_join(sensor.run)

        logger.info('running wamp')
        print('running wamp')
        autobahn.asyncio.component.run([wamp_component])


