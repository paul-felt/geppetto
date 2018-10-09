import argparse
import logging
import time
import requests
import asyncio

from autobahn.asyncio.component import Component, run
from geppetto_client import Control, Sensor, Register

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(level=logging.ERROR)

class DummySensor(Sensor):
    def get_mediatype(self):
        return 'video'
    def get_reading(self):
        return time.time()

class DummyControl(Control):
    def get_limits(self):
        return 0,180
    def apply_control(self,signal):
        print('applying control: %s: %s'%(self.channel_name, signal))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost', help='The host that geppetto is running on')
    parser.add_argument('--web-port', default=80, type=int, help='The port that the geppetto web server is running on')
    parser.add_argument('--wamp-port', default=8080, type=int, help='The port that the geppetto wamp server is running on')
    args = parser.parse_args()


    # 1) create a wamp session and define callbacks
    component = Component(
        transports=u"ws://{host}:{port}/ws".format(host=args.host, port=args.wamp_port),
        realm=u"realm1",
    )

    # Register is in charge of adding/removing robots from the rest api
    with Register(args.host, args.web_port, args.wamp_port) as register:

        register.add_sensor (DummySensor ('mock-robot1','sensor1'))
        register.add_sensor (DummySensor ('mock-robot1','sensor2'))
        register.add_control(DummyControl('mock-robot1','control1'))
        register.add_control(DummyControl('mock-robot1','control2'))

        register.add_sensor (DummySensor ('mock-robot2','sensor1'))
        register.add_sensor (DummySensor ('mock-robot2','sensor2'))
        register.add_control(DummyControl('mock-robot2','control1'))
        register.add_control(DummyControl('mock-robot2','control2'))
        register.run()

    #    # 2) callback: define robots after we join a wamp session
    #    @component.on_join
    #    async def on_wamp_join(session, details):

    #        # fire up the sensors
    #        for sensor in [
    #                        DummySensor('mock-robot1','sensor1'), 
    #                        DummySensor('mock-robot1','sensor2'),
    #                        DummySensor('mock-robot2','sensor1'), 
    #                        DummySensor('mock-robot2','sensor2'),
    #                      ]:
    #            register.add_sensor(sensor)
    #            sensor.run(session)

    #        # fire up the controls
    #        for control in [
    #                        DummyControl('mock-robot1','control1'), 
    #                        DummyControl('mock-robot1','control2'),
    #                        DummyControl('mock-robot2','control1'), 
    #                        DummyControl('mock-robot2','control2'),
    #                       ]:
    #            register.add_control(control)
    #            control.run(session)

    ## 3) get the ball rolling by actually firing up the wamp server
    #run([component])
