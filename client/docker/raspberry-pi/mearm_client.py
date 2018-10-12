import argparse
import logging
import geppetto_client
from geppetto_client import Control, Sensor, Robot
from picam_sensor import PicamSensor
from adafruit_pca9685_control import AdaFruitPCA9685Control

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost', help='The host that geppetto is running on')
    parser.add_argument('--web-port', default=8080, type=int, help='The port that the geppetto web server is running on')
    parser.add_argument('--wamp-port', default=5555, type=int, help='The port that the geppetto wamp server is running on')
    args = parser.parse_args()

    # Robot is in charge of adding/removing robots from the rest api
    with Robot(args.host, args.web_port, args.wamp_port) as robot:
        # Picam sensor
        robot.add_sensor(PicamSensor('marion', 'picam'))
    	### Mearm controls
        robot.add_control(AdaFruitPCA9685Control('marion', 'twist', 0, min_limit=100, max_limit=500))
        robot.add_control(AdaFruitPCA9685Control('marion', 'height', 1, min_limit=150, max_limit=280))
        robot.add_control(AdaFruitPCA9685Control('marion', 'forward', 2, min_limit=280, max_limit=450))
        robot.add_control(AdaFruitPCA9685Control('marion', 'claw', 3, min_limit=150, max_limit=370))
        # interleave control/sensor logic with asyncio
        #robot.start_with_asyncio()
        # run each control/sensor in its own process
        robot.start_with_multiprocessing()

