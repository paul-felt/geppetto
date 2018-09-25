import logging
import multiprocessing
import time
from socketIO_client import SocketIO, LoggingNamespace

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)

sensors = []
def register_sensor(sensor):
    sensors.append(sensor)
    sensor.start()

controls = []
def register_control(control):
    controls.append(control)
    control.start()

class Signal(multiprocessing.Process):
    def __init__(self, robot_name, signal_name):
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
        with SocketIO('localhost', 5555) as socketIO:
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
    def __init__(self, robot_name, sensor_name):
        super(DummySensor, self).__init__(robot_name, sensor_name)
    def get_mediatype(self):
        return 'video'
    def get_reading(self):
        time.sleep(30)
        return time.time()

class DummyControl(Control):
    def __init__(self, robot_name, control_name):
        super(DummyControl, self).__init__(robot_name, control_name)
    def get_limits(self):
        return 0,180
    def apply_control(self,signal):
        print 'applying control: %s: %s'%(self.get_socketio_name(),signal)

for sensor in [
            DummySensor('mock-robot1','sensor1'), 
            DummySensor('mock-robot1','sensor2'),
            DummySensor('mock-robot2','sensor1'),
            DummySensor('mock-robot2','sensor2'),
            ]:
    register_sensor(sensor)
    
for control in [
            DummyControl('mock-robot1','control1'), 
            DummyControl('mock-robot1','control2'),
            DummyControl('mock-robot2','control1'), 
            DummyControl('mock-robot2','control2'),
            ]:
    register_control(control)

