import argparse
import logging
import time
import requests
import asyncio
import signal
import os
import sys
from multiprocessing import Process

from autobahn.asyncio import component as autobahn_utils

import constants

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class Signal(object):
    def __init__(self, robot_name, name):
        self.robot_name = robot_name
        self.name = name
    def get_channel_name(self):
        raise NotImplementedError()
    def __repr__(self):
        return self.get_channel_name()
    def cleanup(self):
        'override this if you need to clean up system resources before exit'
        pass 

class Control(Signal):
    def __init__(self, robot_name, name):
        super().__init__(robot_name, name)
        self.channel_name = self.get_channel_name()
    def get_channel_name(self):
        return 'gp.robots.{}.controls.{}'.format(self.robot_name, self.name)
    def get_limits(self):
        raise NotImplementedError()
    def apply_control_value(self,control_value):
        raise NotImplementedError()
    def apply_control(self,*args,**control_info):
        # get the control value
        control_value = int(float(control_info['value']))
        # make sure it's within limits
        min_limit, max_limit = self.get_limits()
        if not (min_limit <= control_value and control_value <= max_limit):
            logger.warn('control value=%s out of range[%s,%s]. Truncating', control_value,self.min_limit,self.max_limit)
            control_value = min(max_limit, control_value)
            control_value = max(min_limit, control_value)
        # pass it on
        self.apply_control_value(control_value)
    async def on_join(self, session, details):
        logger.info('subscribing to control: %s',self.channel_name)
        self.subscription = await session.subscribe(self.apply_control, self.channel_name)
    async def on_leave(self, session, details):
        logger.info('unsubscribing to control: %s',self.channel_name)
        if hasattr(self, 'subscription'):
            await self.subscription.unsubscribe()


class Sensor(Signal):
    def __init__(self, robot_name, name, refresh=0.05):
        super().__init__(robot_name, name)
        self.refresh = refresh
        self.channel_name = self.get_channel_name()
    def get_channel_name(self):
        return 'gp.robots.{}.sensors.{}'.format(self.robot_name, self.name)
    def get_source(self):
        return 'robot'
    def get_reading(self):
        raise NotImplementedError()
    def get_mediatype(self):
        raise NotImplementedError()
    async def on_join(self, session, details):
        logger.info('publishing to sensor: %s',self.channel_name)
        self.publishing = True
        while self.publishing:
            msg = {
                constants.SIGNAL_VALUE : self.get_reading(),
                constants.SIGNAL_ROBOT_NAME : self.robot_name,
                constants.SIGNAL_NAME : self.name,
                constants.SIGNAL_SOURCE : self.get_source(),
                constants.SIGNAL_TYPE : constants.SIGNAL_TYPE_SENSOR,
                constants.SIGNAL_MEDIATYPE : self.get_mediatype(),
                constants.SIGNAL_TS : int(time.time()*1000)
            }
            session.publish(self.channel_name, **msg)
            await asyncio.sleep(self.refresh)
    async def on_leave(self, session, details):
        logger.info('ceased publishing to sensor: %s',self.channel_name)
        self.publishing = False
        self.cleanup()

class Register(object):
    def __init__(self, host, web_port, wamp_port):
        self.host = host
        self.web_port = web_port
        self.wamp_port = wamp_port
        self.sensors = set([])
        self.controls = set([])

    def base_url(self):
        return "http://{host}:{port}/robots".format(
            host=self.host,
            port=self.web_port,
        )

    def robot_url(self, robot_name):
        return "{base_url}/{robot_name}".format(
            base_url=self.base_url(),
            robot_name=robot_name,
        )

    def control_url(self, robot_name, name):
        return "{robot_url}/controls/{name}".format(
            robot_url=self.robot_url(robot_name),
            name=name,
        )

    def sensor_url(self, robot_name, name):
        return "{robot_url}/sensors/{name}".format(
            robot_url=self.robot_url(robot_name),
            name=name,
        )

    def registered_robot_names(self):
        robot_names = set([sig.robot_name for sig in self.controls])
        robot_names = robot_names.union(set([sig.robot_name for sig in self.sensors]))
        return robot_names

    def registered_control_names(self):
        return set([sig.name for sig in self.controls])

    def registered_sensor_names(self):
        return set([sig.name for sig in self.sensors])

    def __enter__(self):
        ' Just make sure the rest interface is responsive by doing some dummy request '
        requests.get("{}/robots".format(self.base_url()))
        return self

    def __exit__(self, type, value, traceback):
        ' Delete from the rest api all sensors and controls in this register '

        # Do we fully define this robot? (no other collaborating controls/sensors running elsewhere)
        for robot_name in self.registered_robot_names():
            robot_url = self.robot_url(robot_name)
            resp = requests.get(robot_url)
            # get remote names
            control_names = [sig[constants.SIGNAL_NAME] for sig in resp.json().get('controls',[])]
            sensor_names = [sig[constants.SIGNAL_NAME] for sig in resp.json().get('sensors',[])]
            # get local names
            my_control_names = [sig.name for sig in self.controls]
            my_sensor_names = [sig.name for sig in self.sensors]
            delete_whole_robot = self.registered_control_names().issuperset(control_names) and self.registered_sensor_names().issuperset(sensor_names)

            # If we fully define this robot, delete the whole thing
            if delete_whole_robot:
                logger.info('DELETE %s', robot_url)
                resp = requests.delete(robot_url)
                logger.info('response: %s', resp.status_code)
                assert resp.status_code == 200, 'control deletion request failed: %s'%resp.text

            # There are other controls/sensors running elsewhere. Only delete the controls/sensors we own
            else:
                # If this unit is only part of the robot, delete the controls/sensors piecemeal
                for sensor in self.sensors:
                    url = self.sensor_url(sensor.robot_name, sensor.name)
                    logger.info('DELETE %s', url)
                    resp = requests.delete(url)
                    logger.info('response: %s', resp.status_code)
                    assert resp.status_code == 200, 'sensor deletion request failed: %s'%resp.text
                    # Note: we can't call sensor.stop() here because we might be 
                    # in a different (parent) process from the actual sensor hardware
                for control in self.controls:
                    url = self.control_url(control.robot_name, control.name)
                    logger.info('DELETE %s', url)
                    resp = requests.delete(url)
                    logger.info('response: %s', resp.status_code)
                    assert resp.status_code == 200, 'control deletion request failed: %s'%resp.text
                    # Note: we can't call control.stop() here because we might be 
                    # in a different (parent) process from the actual wamp session 

    def add_sensor(self, sensor):
        url = self.sensor_url(sensor.robot_name, sensor.name)
        logger.info('POST: %s to %s', sensor.channel_name, url)
        resp = requests.post(url, json = {'channel_name':sensor.channel_name,
                                    'mediatype':sensor.get_mediatype()})
        logger.info('response: %s', resp.status_code)
        assert resp.status_code == 200, 'sensor creation request failed: %s'%resp.text
        self.sensors.add(sensor)

    def add_control(self, control):
        url = self.control_url(control.robot_name, control.name)
        logger.info('POST: %s to %s', control.channel_name, url)
        resp = requests.post(url, json = {'channel_name':control.channel_name,
                                    'limits':control.get_limits()})
        assert resp.status_code == 200, 'control creation request failed: %s'%resp.text
        logger.info('response: %s', resp.status_code)
        self.controls.add(control)

    def _get_wamp_component(self):
        # define a wamp component with settings matching
        # the vanilla server settings (no special needs here)
        return autobahn_utils.Component(
            transports=u"ws://{host}:{port}/ws".format(host=self.host, port=self.wamp_port),
            realm=u"realm1",
        )

    def start_with_asyncio(self):
        wamp_component = self._get_wamp_component()

        # callback controls
        for control in self.controls:
            wamp_component.on_join(control.on_join)
            wamp_component.on_leave(control.on_leave)

        # callback sensors
        for sensor in self.sensors:
            wamp_component.on_join(sensor.on_join)
            wamp_component.on_leave(sensor.on_leave)

        autobahn_utils.run([wamp_component])

    def start_with_multiprocessing(self):
        def worker(robot_signal):
            # now create a wamp connection and run the signal (sensor/control)
            wamp_component = self._get_wamp_component()
            wamp_component.on_join(robot_signal.on_join)
            wamp_component.on_leave(robot_signal.on_leave)
            # first register to handle SIGINT so we can shutdown cleanly
            def on_shutdown(sig, frame):
                # this calls on_leave, which calls sensor.cleanup()
                wamp_component.stop()
            signal.signal(signal.SIGUSR1, on_shutdown)
            autobahn_utils.run([wamp_component])

        processes = []
        # callback controls
        for control in self.controls:
            processes.append(Process(target=worker, args=(control,)))

        # callback sensors
        for sensor in self.sensors:
            processes.append(Process(target=worker, args=(sensor,)))

        # run worker processes 
        for process in processes:
            process.start()

        # relay any shutdown (sigint) request into the subprocesses
        # so they can release any hardware and shutdown cleanly
        # Note: we'll relay as a SIGUSR1 signal, since SIGINT and 
        # SIGTERM have special meaning and handling and tend to cause
        # all manner of problems.
        def on_shutdown_master(sig, frame):
            for process in processes:
                os.kill(process.pid, signal.SIGUSR1)
        signal.signal(signal.SIGINT, on_shutdown_master)
        signal.signal(signal.SIGTERM, on_shutdown_master)

        # wait for them to terminate
        for process in processes:
            process.join()
        
