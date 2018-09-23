import logging
import multiprocessing
import time
from socketIO_client import SocketIO, LoggingNamespace

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)

sensors = []
def register_sensor(sensor):
    sensors.append(sensor)
    sensor.start()

controls = []
def register_control(control):
    controls.append(control)
    control.start()

class Signal(multiprocessing.Process):
    def get_name(self):
        raise NotImplementedError()
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
        socketIO.emit('register-control', {'name':self.get_name(),
                                        'limits':self.get_limits()})
    def run_with_socket(self, socketIO):
        socketIO.on(self.get_name(),self.apply_control)
        socketIO.wait()

class Sensor(Signal):
    def get_reading(self):
        raise NotImplementedError()
    def get_type(self):
        raise NotImplementedError()
    def register_signal(self,socketIO):
        socketIO.emit('register-sensor', {'name':self.get_name(),
                                        'type':self.get_type()})
    def run_with_socket(self, socketIO):
        while True:
            socketIO.emit('sensor', {self.get_name(): self.get_reading()})

class DummySensor(Sensor):
    def __init__(self,idx):
        self.idx = idx
        super(DummySensor, self).__init__()
    def get_name(self):
        time.sleep(1)
        return 'sensor duh-vice %s' % self.idx
    def get_type(self):
        return 'video'
    def get_reading(self):
        return time.time()

class DummyControl(Control):
    def __init__(self, idx):
        self.idx = idx
        super(DummyControl, self).__init__()
    def get_name(self):
        return 'control duh-vice %s' % self.idx
    def get_limits(self):
        return 0,180
    def apply_control(self,signal):
        print 'applying control: %s'%signal

for sensor in [DummySensor(1), DummySensor(2)]:
    register_sensor(sensor)
    
for control in [DummyControl(1), DummyControl(2)]:
    register_control(control)

