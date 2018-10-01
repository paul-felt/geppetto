import argparse
import logging
#from multiprocessing import Process
from threading import Thread as Process
import time
from socketIO_client import SocketIO, LoggingNamespace

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(level=logging.ERROR)

sensors = []
def register_sensor(sensor):
    sensors.append(sensor)
    sensor.start()

controls = []
def register_control(control):
    controls.append(control)
    control.start()

class Signal(Process):
    def __init__(self, host, port, robot_name, signal_name):
        self.host=host
        self.port=port
        self.robot_name = robot_name
        self.signal_name = signal_name
        super(Signal, self).__init__()
    def get_socketio_name(self):
        return '{}-{}'.format(self.robot_name, self.signal_name)
    def run_with_socket(self,socketIO):
        raise NotImplementedError()
    def register_signal(self,socketIO):
        raise NotImplementedError()
    def run(self):
        with SocketIO(self.host, self.port) as socketIO:
            self.register_signal(socketIO)
            self.run_with_socket(socketIO)

class Control(Signal):
    def apply_control(self,signal):
        raise NotImplementedError()
    def get_limits(self):
        raise NotImplementedError()
    def register_signal(self,socketIO):
        socketIO.emit('register-control', {
                                        'robot_name':self.robot_name,
                                        'control_name':self.signal_name,
                                        'socketio_name':self.get_socketio_name(),
                                        'limits':self.get_limits()})
    def run_with_socket(self, socketIO):
        socketIO.on(self.get_socketio_name(),self.apply_control)
        socketIO.wait()

class Sensor(Signal):
    def get_reading(self):
        raise NotImplementedError()
    def get_mediatype(self):
        raise NotImplementedError()
    def register_signal(self,socketIO):
        socketIO.emit('register-sensor', {
                                        'robot_name':self.robot_name,
                                        'sensor_name':self.signal_name,
                                        'socketio_name':self.get_socketio_name(),
                                        'mediatype':self.get_mediatype()})
    def run_with_socket(self, socketIO):
        while True:
            socketIO.emit('sensor', (self.get_socketio_name(), self.get_reading()))

class DummySensor(Sensor):
    def get_mediatype(self):
        return 'video'
    def get_reading(self):
        time.sleep(30)
        return time.time()

class DummyControl(Control):
    def get_limits(self):
        return 0,180
    def apply_control(self,signal):
        print('applying control: %s: %s'%(self.get_socketio_name(),signal))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhostl', help='The host that geppetto is running on')
    parser.add_argument('-p', '--port', default=5000, type=int, help='The port that geppetto is running on')
    args = parser.parse_args()

    for sensor in [
                DummySensor(args.host, args.port, 'mock-robot1','sensor1'), 
                DummySensor(args.host, args.port, 'mock-robot1','sensor2'),
                DummySensor(args.host, args.port, 'mock-robot2','sensor1'),
                DummySensor(args.host, args.port, 'mock-robot2','sensor2'),
                ]:
        register_sensor(sensor)
        
    for control in [
                DummyControl(args.host, args.port, 'mock-robot1','control1'), 
                DummyControl(args.host, args.port, 'mock-robot1','control2'),
                DummyControl(args.host, args.port, 'mock-robot2','control1'), 
                DummyControl(args.host, args.port, 'mock-robot2','control2'),
                ]:
        register_control(control)

