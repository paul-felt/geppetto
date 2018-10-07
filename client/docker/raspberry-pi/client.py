import argparse
import logging
import geppetto_client
from geppetto_client import DummySensor, DummyControl
from picam_sensor import PicamSensor
from adafruit_pca9685_control import AdaFruitPCA9685Control

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhostl', help='The host that geppetto is running on')
    parser.add_argument('--web-port', default=80, type=int, help='The port that the geppetto web server is running on')
    parser.add_argument('--wamp-port', default=5555, type=int, help='The port that geppetto wamp server is running on')
    args = parser.parse_args()

#    for sensor in [
#                DummySensor(args.host, args.web_port, args.wamp_port, 'mock-robot1','sensor1'), 
#                DummySensor(args.host, args.web_port, args.wamp_port, 'mock-robot1','sensor2'),
#                DummySensor(args.host, args.web_port, args.wamp_port, 'mock-robot2','sensor1'),
#                DummySensor(args.host, args.web_port, args.wamp_port, 'mock-robot2','sensor2'),
#                ]:
#        geppetto_client.register_sensor(sensor)

    for control in [
                DummyControl(args.host, args.web_port, args.wamp_port, 'mock-robot1','control1'), 
    #            DummyControl(args.host, args.web_port, args.wamp_port, 'mock-robot1','control2'),
    #            DummyControl(args.host, args.web_port, args.wamp_port, 'mock-robot2','control1'), 
    #            DummyControl(args.host, args.web_port, args.wamp_port, 'mock-robot2','control2'),
    #            ]:
        geppetto_client.register_control(control)

    #geppetto_client.register_sensor(PicamSensor(args.host, args.web_port, args.wamp_port, 'marion', 'picam'))
    ## Mearm controls
    #geppetto_client.register_control(AdaFruitPCA9685Control(args.host, args.web_port, args.wamp_port, 'marion', 'twist', 0, min_limit=350, max_limit=450))
    #geppetto_client.register_control(AdaFruitPCA9685Control(args.host, args.web_port, args.wamp_port, 'marion', 'height', 1, min_limit=150, max_limit=280))
    #geppetto_client.register_control(AdaFruitPCA9685Control(args.host, args.web_port, args.wamp_port, 'marion', 'forward', 2, min_limit=280, max_limit=450))
    #geppetto_client.register_control(AdaFruitPCA9685Control(args.host, args.web_port, args.wamp_port, 'marion', 'claw', 3, min_limit=150, max_limit=370))
 
